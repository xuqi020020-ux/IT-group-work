# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from django.contrib.auth.models import User

from django.utils import timezone
from .models import Document, DocumentShare, EditSuggestion
from .forms import DocumentForm, ShareForm, SuggestionForm


from django.db.models import Q

def can_view_document(user, doc):
    # Admin: can view all docs
    if user.is_staff:
        return True

    # Owner: can always view their own docs (including moderated)
    if doc.owner_id == user.id:
        return True

    # Moderated: not visible to non-owner
    if doc.visibility_status == Document.VIS_MODERATED:
        return False

    # Public: visible to any logged-in user
    if doc.visibility_status == Document.VIS_PUBLIC:
        return True

    # Shared: visible if shared with user
    if doc.visibility_status == Document.VIS_SHARED:
        return DocumentShare.objects.filter(document=doc, shared_with=user).exists()

    # Private: only owner (already handled)
    return False

@login_required
def shared_with_me(request):
    if request.user.is_staff:
        # Admin doesn't need this view; keep it simple
        docs = Document.objects.none()
    else:
        shared_ids = DocumentShare.objects.filter(
            shared_with=request.user
        ).values_list("document_id", flat=True)

        docs = Document.objects.filter(
            id__in=shared_ids,
            visibility_status=Document.VIS_SHARED
        ).exclude(visibility_status=Document.VIS_MODERATED).order_by("-updated_at")

        for d in docs:
            d.access_label = "Shared"

    return render(request, "core/shared_with_me.html", {"documents": docs})


@login_required
def dashboard(request):
    q = request.GET.get("q", "").strip()

    # Admin can see all documents (including moderated)
    if request.user.is_staff:
        docs = Document.objects.all()
    else:
        # Accessible docs:
        # - owned by user
        # - public
        # - shared with user
        shared_doc_ids = DocumentShare.objects.filter(
            shared_with=request.user
        ).values_list("document_id", flat=True)

        docs = Document.objects.filter(
            Q(owner=request.user) |
            Q(visibility_status=Document.VIS_PUBLIC) |
            Q(id__in=shared_doc_ids)
        ).exclude(
            visibility_status=Document.VIS_MODERATED
        )

    if q:
        docs = docs.filter(
            Q(title__icontains=q) |
            Q(owner__username__icontains=q)
        )

    docs = docs.order_by("-updated_at").distinct()


    # Build a quick lookup to label "Shared" docs
    shared_ids = set()
    if not request.user.is_staff:
        shared_ids = set(DocumentShare.objects.filter(
            shared_with=request.user
        ).values_list("document_id", flat=True))

    doc_sources = {}

    if not request.user.is_staff:
        shared_ids = set(DocumentShare.objects.filter(
            shared_with=request.user
        ).values_list("document_id", flat=True))
    else:
        shared_ids = set()

    for d in docs:
        if d.owner_id == request.user.id:
            d.access_label = "Owned"
        elif d.visibility_status == Document.VIS_PUBLIC:
            d.access_label = "Public"
        elif d.id in shared_ids:
            d.access_label = "Shared"
        else:
            d.access_label = "Accessible"

    return render(request, "core/dashboard.html", {"documents": docs, "q": q})


#    for d in docs:
#        if d.owner_id == request.user.id:
#            doc_sources[d.id] = "Owned"
#        elif d.visibility_status == Document.VIS_PUBLIC:
#            doc_sources[d.id] = "Public"
#        elif d.id in shared_ids:
#            doc_sources[d.id] = "Shared"
#        else:
#            doc_sources[d.id] = "Accessible"


#    return render(request, "core/dashboard.html", {"documents": docs, "q": q, "doc_sources": doc_sources})


@login_required
def document_detail(request, pk):

    doc = get_object_or_404(Document, pk=pk)
    if not can_view_document(request.user, doc):
        return HttpResponseForbidden("You do not have permission to view this document.")


    return render(request, "core/document_detail.html", {"document": doc})


@login_required
def document_create(request):
    if request.method == "POST":
        form = DocumentForm(request.POST)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.owner = request.user
            doc.save()
            return redirect("core:document_detail", pk=doc.pk)
    else:
        form = DocumentForm()
    return render(request, "core/document_form.html", {"form": form, "mode": "Create"})


@login_required
def document_edit(request, pk):
    
    doc = get_object_or_404(Document, pk=pk)
    if not (request.user.is_staff or doc.owner_id == request.user.id):
        return HttpResponseForbidden("You do not have permission to edit this document.")

    if request.method == "POST":
        form = DocumentForm(request.POST, instance=doc)
        if form.is_valid():
            form.save()
            return redirect("core:document_detail", pk=doc.pk)
    else:
        form = DocumentForm(instance=doc)
    return render(request, "core/document_form.html", {"form": form, "mode": "Edit"})


@login_required
def document_delete(request, pk):

    doc = get_object_or_404(Document, pk=pk)
    if not (request.user.is_staff or doc.owner_id == request.user.id):
        return HttpResponseForbidden("You do not have permission to delete this document.")

    if request.method == "POST":
        doc.delete()
        return redirect("core:dashboard")
    return render(request, "core/document_confirm_delete.html", {"document": doc})

@login_required
def document_share(request, pk):
    doc = get_object_or_404(Document, pk=pk)

    # Only owner or admin can manage shares
    if not (request.user.is_staff or doc.owner_id == request.user.id):
        return HttpResponseForbidden("You do not have permission to share this document.")

    # Only meaningful for shared visibility (optional rule)
    # If you prefer, you can allow sharing for any doc but it only takes effect when visibility=shared.
    from .forms import ShareForm
    form = ShareForm(request.POST or None)

    message = None

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"].strip()

        if username == doc.owner.username:
            message = "You cannot share a document with its owner."
        else:
            target = User.objects.filter(username=username).first()
            if not target:
                message = "User not found."
            else:
                DocumentShare.objects.get_or_create(document=doc, shared_with=target)
                message = "Shared successfully."

    shares = DocumentShare.objects.filter(document=doc).select_related("shared_with").order_by("shared_with__username")

    return render(request, "core/document_share.html", {
        "document": doc,
        "form": form,
        "shares": shares,
        "message": message,
    })


@login_required
def document_unshare(request, pk, user_id):
    doc = get_object_or_404(Document, pk=pk)

    # Only owner or admin can unshare
    if not (request.user.is_staff or doc.owner_id == request.user.id):
        return HttpResponseForbidden("You do not have permission to manage shares for this document.")

    if request.method != "POST":
        return HttpResponseForbidden("Invalid request method.")

    DocumentShare.objects.filter(document=doc, shared_with_id=user_id).delete()
    return redirect("core:document_share", pk=doc.pk)

@login_required
def suggestion_create(request, pk):
    doc = get_object_or_404(Document, pk=pk)

    # Must be able to view the document
    if not can_view_document(request.user, doc):
        return HttpResponseForbidden("You do not have permission to access this document.")

    # Owner doesn't need to suggest edits on their own doc
    if doc.owner_id == request.user.id:
        return HttpResponseForbidden("Owners cannot submit suggestions for their own documents.")

    # Only allow suggestions for public or shared docs (shared-with-me)
    if not (doc.visibility_status == Document.VIS_PUBLIC or doc.visibility_status == Document.VIS_SHARED):
        return HttpResponseForbidden("Suggestions are only allowed for public/shared documents.")

    # If shared, ensure actually shared with the user (can_view_document already implies this)
    form = SuggestionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        EditSuggestion.objects.create(
            document=doc,
            proposer=request.user,
            proposed_content=form.cleaned_data["proposed_content"],
            status=EditSuggestion.STATUS_PENDING,
        )
        return redirect("core:document_detail", pk=doc.pk)

    # Prefill with current content for easier editing
    if request.method == "GET":
        form = SuggestionForm(initial={"proposed_content": doc.content})

    return render(request, "core/suggestion_form.html", {"document": doc, "form": form})


@login_required
def suggestion_review_list(request):
    # Owner sees suggestions on their documents; admin can see all (optional)
    if request.user.is_staff:
        qs = EditSuggestion.objects.filter(status=EditSuggestion.STATUS_PENDING)
    else:
        qs = EditSuggestion.objects.filter(
            status=EditSuggestion.STATUS_PENDING,
            document__owner=request.user
        )

    qs = qs.select_related("document", "proposer").order_by("-created_at")
    return render(request, "core/suggestion_review_list.html", {"suggestions": qs})


@login_required
def suggestion_review_action(request, sid):
    sug = get_object_or_404(EditSuggestion, pk=sid)
    doc = sug.document

    # Only owner of the document (or admin) can review
    if not (request.user.is_staff or doc.owner_id == request.user.id):
        return HttpResponseForbidden("You do not have permission to review this suggestion.")

    if request.method != "POST":
        return HttpResponseForbidden("Invalid request method.")

    action = request.POST.get("action")

    if sug.status != EditSuggestion.STATUS_PENDING:
        return redirect("core:suggestion_review_list")

    if action == "accept":
        doc.content = sug.proposed_content
        doc.save()
        sug.status = EditSuggestion.STATUS_ACCEPTED
        sug.reviewed_at = timezone.now()
        sug.save()
    elif action == "reject":
        sug.status = EditSuggestion.STATUS_REJECTED
        sug.reviewed_at = timezone.now()
        sug.save()

    return redirect("core:suggestion_review_list")

