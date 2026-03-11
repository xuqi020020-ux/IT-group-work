from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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


    moderated_reason = models.CharField(max_length=255, blank=True)



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


class DocumentAttachment(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_attachments",
    )
    file = models.FileField(upload_to="attachments/%Y/%m/")
    original_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return "Attachment {} for Doc {}".format(self.id, self.document_id)

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    nickname = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # User preference settings fields
    page_zoom = models.IntegerField(default=100)       # Page zoom ratio (%)
    text_size = models.IntegerField(default=16)        # Text size (px)
    brightness = models.IntegerField(default=100)      # Brightness (%)

    tts_enabled = models.BooleanField(default=False)   # Text-to-speech feature toggle

    def __str__(self):
        return f"{self.user.username}'s Profile"
    @property
    def has_unread_notifications(self):
        return self.user.notifications.filter(is_read=False).exists()

# Signal: When a User is created, a UserProfile is automatically created for that User.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Associated to a specific document; 
    # if the document is deleted, set to NULL. Notification history is retained.
    related_document = models.ForeignKey(
        Document, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.recipient.username}: {self.message}"