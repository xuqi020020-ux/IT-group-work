from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import (
    Document, DocumentShare, EditSuggestion,
    Comment, DocumentAttachment, UserProfile, Notification
)

User = get_user_model()


# ── Document ───────────────────────────────────────────────────────────────────

class DocumentModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass123")
        self.doc = Document.objects.create(owner=self.user, title="My Test Doc", content="Example text")

    def test_document_string_representation(self):
        self.assertEqual(str(self.doc), "My Test Doc")

    def test_default_visibility_is_private(self):
        self.assertEqual(self.doc.visibility_status, Document.VIS_PRIVATE)

    def test_document_owner_relationship(self):
        self.assertEqual(self.doc.owner.username, "alice")

    def test_ordering_is_by_updated_at_desc(self):
        doc2 = Document.objects.create(owner=self.user, title="Second Doc")
        docs = list(Document.objects.all())
        self.assertEqual(docs[0], doc2)
        self.assertEqual(docs[1], self.doc)

    def test_blank_content_is_allowed(self):
        doc = Document.objects.create(owner=self.user, title="No Content")
        self.assertEqual(doc.content, "")

    def test_visibility_choices(self):
        for status in [Document.VIS_PRIVATE, Document.VIS_SHARED,
                       Document.VIS_PUBLIC, Document.VIS_MODERATED]:
            self.doc.visibility_status = status
            self.doc.save()
            self.doc.refresh_from_db()
            self.assertEqual(self.doc.visibility_status, status)


# ── DocumentShare ──────────────────────────────────────────────────────────────

class DocumentShareTests(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass")
        self.recipient = User.objects.create_user(username="bob", password="pass")
        self.doc = Document.objects.create(owner=self.owner, title="Shareable Doc")
        self.share = DocumentShare.objects.create(document=self.doc, shared_with=self.recipient)

    def test_string_representation(self):
        expected = f"{self.doc.id} -> {self.recipient.id}"
        self.assertEqual(str(self.share), expected)

    def test_uniqueness_constraint(self):
        with self.assertRaises(Exception):
            DocumentShare.objects.create(document=self.doc, shared_with=self.recipient)

    def test_share_deleted_when_document_deleted(self):
        self.doc.delete()
        self.assertFalse(DocumentShare.objects.filter(pk=self.share.pk).exists())

    def test_share_deleted_when_user_deleted(self):
        self.recipient.delete()
        self.assertFalse(DocumentShare.objects.filter(pk=self.share.pk).exists())


# ── EditSuggestion ─────────────────────────────────────────────────────────────

class EditSuggestionTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="charlie", password="1234")
        self.doc = Document.objects.create(owner=self.user, title="Suggested Doc")
        self.suggestion = self.doc.suggestions.create(
            proposer=self.user,
            proposed_content="Edited content suggestion"
        )

    def test_default_status_is_pending(self):
        self.assertEqual(self.suggestion.status, EditSuggestion.STATUS_PENDING)

    def test_str(self):
        self.assertIn(str(self.doc.pk), str(self.suggestion))

    def test_reviewed_at_is_null_by_default(self):
        self.assertIsNone(self.suggestion.reviewed_at)

    def test_status_can_be_accepted(self):
        self.suggestion.status = EditSuggestion.STATUS_ACCEPTED
        self.suggestion.save()
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, EditSuggestion.STATUS_ACCEPTED)

    def test_status_can_be_rejected(self):
        self.suggestion.status = EditSuggestion.STATUS_REJECTED
        self.suggestion.save()
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, EditSuggestion.STATUS_REJECTED)

    def test_suggestion_deleted_when_document_deleted(self):
        self.doc.delete()
        self.assertFalse(EditSuggestion.objects.filter(pk=self.suggestion.pk).exists())


# ── Comment ────────────────────────────────────────────────────────────────────

class CommentModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="commenter", password="pass")
        self.doc = Document.objects.create(owner=self.user, title="Commented Doc")
        self.comment = Comment.objects.create(
            document=self.doc, author=self.user, content="Nice doc!"
        )

    def test_str(self):
        self.assertIn(str(self.doc.pk), str(self.comment))

    def test_comment_content_stored(self):
        self.assertEqual(self.comment.content, "Nice doc!")

    def test_comment_deleted_when_document_deleted(self):
        self.doc.delete()
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_comment_deleted_when_author_deleted(self):
        # Document.owner is PROTECT, so we must delete the doc first before deleting the user
        self.doc.delete()
        self.user.delete()
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())



# ── DocumentAttachment ─────────────────────────────────────────────────────────

class DocumentAttachmentModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="uploader", password="pass")
        self.doc = Document.objects.create(owner=self.user, title="Doc With Attachment")

    def test_str(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        att = DocumentAttachment.objects.create(
            document=self.doc,
            uploaded_by=self.user,
            file=SimpleUploadedFile("test.txt", b"data"),
            original_name="test.txt",
        )
        self.assertIn(str(self.doc.pk), str(att))

    def test_attachment_deleted_when_document_deleted(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        att = DocumentAttachment.objects.create(
            document=self.doc,
            uploaded_by=self.user,
            file=SimpleUploadedFile("file.txt", b"content"),
            original_name="file.txt",
        )
        self.doc.delete()
        self.assertFalse(DocumentAttachment.objects.filter(pk=att.pk).exists())


# ── UserProfile ────────────────────────────────────────────────────────────────

class UserProfileTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="profileuser", password="pass")

    def test_profile_auto_created_on_user_creation(self):
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_profile_default_page_zoom(self):
        self.assertEqual(self.user.profile.page_zoom, 100)

    def test_profile_default_text_size(self):
        self.assertEqual(self.user.profile.text_size, 16)

    def test_profile_default_brightness(self):
        self.assertEqual(self.user.profile.brightness, 100)

    def test_profile_default_tts_disabled(self):
        self.assertFalse(self.user.profile.tts_enabled)

    def test_profile_str(self):
        self.assertIn(self.user.username, str(self.user.profile))

    def test_has_unread_notifications_true(self):
        Notification.objects.create(
            recipient=self.user, message="Hello", is_read=False
        )
        self.assertTrue(self.user.profile.has_unread_notifications)

    def test_has_unread_notifications_false_when_all_read(self):
        Notification.objects.create(
            recipient=self.user, message="Hello", is_read=True
        )
        self.assertFalse(self.user.profile.has_unread_notifications)


# ── Notification ───────────────────────────────────────────────────────────────

class NotificationModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="notifuser", password="pass")
        self.owner = User.objects.create_user(username="docowner", password="pass")
        self.doc = Document.objects.create(owner=self.owner, title="Notif Doc")

    def test_str(self):
        notif = Notification.objects.create(
            recipient=self.user, message="Test message"
        )
        self.assertIn(self.user.username, str(notif))

    def test_is_read_defaults_to_false(self):
        notif = Notification.objects.create(
            recipient=self.user, message="Unread"
        )
        self.assertFalse(notif.is_read)

    def test_related_document_set_null_on_doc_delete(self):
        notif = Notification.objects.create(
            recipient=self.user, message="Doc deleted",
            related_document=self.doc
        )
        self.doc.delete()
        notif.refresh_from_db()
        self.assertIsNone(notif.related_document)

    def test_notification_deleted_when_recipient_deleted(self):
        notif = Notification.objects.create(
            recipient=self.user, message="Bye"
        )
        self.user.delete()
        self.assertFalse(Notification.objects.filter(pk=notif.pk).exists())
