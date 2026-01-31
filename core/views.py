# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .models import Document
from .forms import DocumentForm


@login_required
def dashboard(request):
    docs = Document.objects.filter(owner=request.user).order_by("-updated_at")
    return render(request, "core/dashboard.html", {"documents": docs})


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

