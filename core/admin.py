from django.contrib import admin
from .models import Document, DocumentShare, EditSuggestion, Comment


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "visibility_status", "updated_at")
    list_filter = ("visibility_status", "created_at", "updated_at")
    search_fields = ("title", "owner__username")

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

