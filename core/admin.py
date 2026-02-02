from django.contrib import admin
from .models import Document, DocumentShare, EditSuggestion, Comment, DocumentAttachment


def moderate_documents(modeladmin, request, queryset):
    queryset.update(
        visibility_status=Document.VIS_MODERATED,
        moderated_reason="Content requires revision (set by admin)."
    )
moderate_documents.short_description = "Moderate selected documents (make non-public)"


def unmoderate_documents(modeladmin, request, queryset):
    queryset.update(
        visibility_status=Document.VIS_PRIVATE,
        moderated_reason=""
    )
unmoderate_documents.short_description = "Unmoderate selected documents (set to private)"

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "visibility_status", "updated_at")
    list_filter = ("visibility_status", "created_at", "updated_at")
    search_fields = ("title", "owner__username")
    actions = [moderate_documents, unmoderate_documents]

@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "shared_with", "created_at")
    search_fields = ("document__title", "shared_with__username")

@admin.register(EditSuggestion)
class EditSuggestionAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "proposer", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("document__title", "proposer__username")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "author", "created_at")
    search_fields = ("document__title", "author__username", "content")
    list_filter = ("created_at",)

@admin.register(DocumentAttachment)
class DocumentAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "uploaded_by", "original_name", "created_at")
    search_fields = ("document__title", "uploaded_by__username", "original_name")

