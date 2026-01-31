from django.conf import settings
from django.db import models


class Document(models.Model):
    VIS_PRIVATE = "private"
    VIS_SHARED = "shared"
    VIS_PUBLIC = "public"
    VIS_MODERATED = "moderated"

    VISIBILITY_CHOICES = (
        (VIS_PRIVATE, "Private"),
        (VIS_SHARED, "Shared"),
        (VIS_PUBLIC, "Public"),
        (VIS_MODERATED, "Moderated"),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="documents",
    )

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    visibility_status = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VIS_PRIVATE,
        db_index=True,
    )

    moderation_reason = models.TextField(blank=True)

    # For user-deletion workflow: track original owner username if ownership is transferred to admin.
    orphaned_from_user = models.CharField(
        max_length=150,
        blank=True,
        help_text="Original owner username if the owner account was deleted.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

class DocumentShare(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="shares",
    )
    shared_with = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="document_access",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("document", "shared_with")

    def __str__(self):
        return "{} -> {}".format(self.document_id, self.shared_with_id)

class EditSuggestion(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    )

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="suggestions",
    )
    proposer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="edit_suggestions",
    )

    proposed_content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return "Suggestion {} for Doc {}".format(self.id, self.document_id)


class Comment(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return "Comment {} on Doc {}".format(self.id, self.document_id)

