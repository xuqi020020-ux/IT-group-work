# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render


from .models import Document, DocumentShare
from .forms import DocumentForm


from django.db.models import Q

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
    return render(request, "core/dashboard.html", {"documents": docs, "q": q})


@login_required
def document_detail(request, pk):
    doc = get_object_or_404(Document, pk=pk, owner=request.user)
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
    doc = get_object_or_404(Document, pk=pk, owner=request.user)
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
    doc = get_object_or_404(Document, pk=pk, owner=request.user)
    if request.method == "POST":
        doc.delete()
        return redirect("core:dashboard")
    return render(request, "core/document_confirm_delete.html", {"document": doc})

