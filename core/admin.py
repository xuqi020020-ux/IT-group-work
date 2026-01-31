from django.contrib import admin
from .models import Document, DocumentShare


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "visibility_status", "updated_at")
    list_filter = ("visibility_status", "created_at", "updated_at")
    search_fields = ("title", "owner__username")

@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "shared_with", "created_at")
    search_fields = ("document__title", "shared_with__username")

