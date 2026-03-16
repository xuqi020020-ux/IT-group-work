from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import (
    Document, DocumentShare, EditSuggestion,
    Comment, DocumentAttachment, Notification
)
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class BaseTestCase(TestCase):
    """Shared setup: owner, other user, admin, and a sample document."""

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username="owner", password="pass")
        self.other = User.objects.create_user(username="other", password="pass")
        self.admin = User.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        self.doc = Document.objects.create(
            owner=self.owner,
            title="Test Doc",
            content="Hello",
            visibility_status=Document.VIS_PRIVATE,
        )

    def login(self, user):
        self.client.force_login(user)


# ── Dashboard ──────────────────────────────────────────────────────────────────

class DashboardViewTests(BaseTestCase):

    def test_dashboard_view_authenticated(self):
        self.login(self.owner)
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertIn(response.status_code, [302, 200])

    def test_redirects_anonymous_to_login(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_owner_sees_own_doc(self):
        self.login(self.owner)
        response = self.client.get(reverse("core:dashboard"))
        self.assertContains(response, "Test Doc")

    def test_other_user_cannot_see_private_doc(self):
        self.login(self.other)
        response = self.client.get(reverse("core:dashboard"))
        self.assertNotContains(response, "Test Doc")

    def test_admin_sees_all_docs(self):
        self.login(self.admin)
        response = self.client.get(reverse("core:dashboard"))
        self.assertContains(response, "Test Doc")

    def test_public_doc_visible_to_others(self):
        self.doc.visibility_status = Document.VIS_PUBLIC
        self.doc.save()
        self.login(self.other)
        response = self.client.get(reverse("core:dashboard"))
        self.assertContains(response, "Test Doc")

    def test_moderated_doc_hidden_from_others(self):
        self.doc.visibility_status = Document.VIS_MODERATED
        self.doc.save()
        self.login(self.other)
        response = self.client.get(reverse("core:dashboard"))
        self.assertNotContains(response, "Test Doc")

    def test_search_filters_by_title(self):
        Document.objects.create(
            owner=self.owner, title="Another Doc",
            visibility_status=Document.VIS_PUBLIC
        )
        self.login(self.other)
        response = self.client.get(reverse("core:dashboard") + "?q=Another")
        self.assertContains(response, "Another Doc")
        self.assertNotContains(response, "Test Doc")

    def test_shared_doc_appears_on_dashboard(self):
        self.doc.visibility_status = Document.VIS_SHARED
        self.doc.save()
        DocumentShare.objects.create(document=self.doc, shared_with=self.other)
        self.login(self.other)
        response = self.client.get(reverse("core:dashboard"))
        self.assertContains(response, "Test Doc")


# ── Document Detail ────────────────────────────────────────────────────────────

class DocumentDetailViewTests(BaseTestCase):

    def test_owner_can_view_private_doc(self):
        self.login(self.owner)
        response = self.client.get(
            reverse("core:document_detail", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Doc")

    def test_other_user_forbidden_on_private_doc(self):
        self.login(self.other)
        response = self.client.get(
            reverse("core:document_detail", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_public_doc_accessible_by_others(self):
        self.doc.visibility_status = Document.VIS_PUBLIC
        self.doc.save()
        self.login(self.other)
        response = self.client.get(
            reverse("core:document_detail", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_shared_doc_accessible_by_shared_user(self):
        self.doc.visibility_status = Document.VIS_SHARED
        self.doc.save()
        DocumentShare.objects.create(document=self.doc, shared_with=self.other)
        self.login(self.other)
        response = self.client.get(
            reverse("core:document_detail", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_moderated_doc_hidden_from_non_owner(self):
        self.doc.visibility_status = Document.VIS_MODERATED
        self.doc.save()
        self.login(self.other)
        response = self.client.get(
            reverse("core:document_detail", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_view_moderated_doc(self):
        self.doc.visibility_status = Document.VIS_MODERATED
        self.doc.save()
        self.login(self.admin)
        response = self.client.get(
            reverse("core:document_detail", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_doc_returns_404(self):
        self.login(self.owner)
        response = self.client.get(
            reverse("core:document_detail", kwargs={"pk": 99999})
        )
        self.assertEqual(response.status_code, 404)


# ── Document Create ────────────────────────────────────────────────────────────

class DocumentCreateViewTests(BaseTestCase):

    def test_create_document_view(self):
        self.login(self.owner)
        response = self.client.post(reverse("core:document_create"), {
            "title": "New Doc",
            "content": "Hello world",
            "visibility_status": Document.VIS_PRIVATE,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Document.objects.filter(title="New Doc").exists())

    def test_get_renders_form(self):
        self.login(self.owner)
        response = self.client.get(reverse("core:document_create"))
        self.assertEqual(response.status_code, 200)

    def test_owner_is_set_to_logged_in_user(self):
        self.login(self.other)
        self.client.post(reverse("core:document_create"), {
            "title": "Others Doc",
            "content": "",
            "visibility_status": Document.VIS_PRIVATE,
        })
        doc = Document.objects.get(title="Others Doc")
        self.assertEqual(doc.owner, self.other)

    def test_invalid_form_does_not_create_document(self):
        self.login(self.owner)
        self.client.post(reverse("core:document_create"), {
            "title": "",
            "content": "No title",
            "visibility_status": Document.VIS_PRIVATE,
        })
        self.assertFalse(Document.objects.filter(content="No title").exists())


# ── Document Edit ──────────────────────────────────────────────────────────────

class DocumentEditViewTests(BaseTestCase):

    def test_edit_document_view(self):
        self.login(self.owner)
        url = reverse("core:document_edit", args=[self.doc.id])
        response = self.client.post(url, {
            "title": "Updated Title",
            "content": "Updated content",
            "visibility_status": Document.VIS_PUBLIC,
        })
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.title, "Updated Title")

    def test_other_user_cannot_edit(self):
        self.login(self.other)
        response = self.client.post(
            reverse("core:document_edit", kwargs={"pk": self.doc.pk}),
            {"title": "Hacked", "content": "", "visibility_status": Document.VIS_PRIVATE}
        )
        self.assertEqual(response.status_code, 403)
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.title, "Test Doc")

    def test_admin_can_edit(self):
        self.login(self.admin)
        self.client.post(
            reverse("core:document_edit", kwargs={"pk": self.doc.pk}),
            {"title": "Admin Edit", "content": "", "visibility_status": Document.VIS_PRIVATE}
        )
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.title, "Admin Edit")

    def test_get_renders_form_for_owner(self):
        self.login(self.owner)
        response = self.client.get(
            reverse("core:document_edit", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 200)


# ── Document Delete ────────────────────────────────────────────────────────────

class DocumentDeleteViewTests(BaseTestCase):

    def test_delete_document_view(self):
        self.login(self.owner)
        url = reverse("core:document_delete", args=[self.doc.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Document.objects.filter(id=self.doc.id).exists())

    def test_other_user_cannot_delete(self):
        self.login(self.other)
        response = self.client.post(
            reverse("core:document_delete", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Document.objects.filter(pk=self.doc.pk).exists())

    def test_admin_can_delete(self):
        self.login(self.admin)
        self.client.post(
            reverse("core:document_delete", kwargs={"pk": self.doc.pk})
        )
        self.assertFalse(Document.objects.filter(pk=self.doc.pk).exists())

    def test_get_renders_confirmation_page(self):
        self.login(self.owner)
        response = self.client.get(
            reverse("core:document_delete", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 200)


# ── Document Share ─────────────────────────────────────────────────────────────

class DocumentShareViewTests(BaseTestCase):

    def test_owner_can_share(self):
        self.login(self.owner)
        self.client.post(
            reverse("core:document_share", kwargs={"pk": self.doc.pk}),
            {"username": self.other.username}
        )
        self.assertTrue(
            DocumentShare.objects.filter(document=self.doc, shared_with=self.other).exists()
        )

    def test_cannot_share_with_nonexistent_user(self):
        self.login(self.owner)
        response = self.client.post(
            reverse("core:document_share", kwargs={"pk": self.doc.pk}),
            {"username": "ghost_user"}
        )
        self.assertContains(response, "User not found")

    def test_cannot_share_with_owner(self):
        self.login(self.owner)
        response = self.client.post(
            reverse("core:document_share", kwargs={"pk": self.doc.pk}),
            {"username": self.owner.username}
        )
        self.assertContains(response, "cannot share")

    def test_other_user_cannot_access_share_view(self):
        self.login(self.other)
        response = self.client.get(
            reverse("core:document_share", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_sharing_same_user_twice_does_not_duplicate(self):
        self.login(self.owner)
        self.client.post(
            reverse("core:document_share", kwargs={"pk": self.doc.pk}),
            {"username": self.other.username}
        )
        self.client.post(
            reverse("core:document_share", kwargs={"pk": self.doc.pk}),
            {"username": self.other.username}
        )
        self.assertEqual(
            DocumentShare.objects.filter(document=self.doc, shared_with=self.other).count(), 1
        )


# ── Document Unshare ───────────────────────────────────────────────────────────

class DocumentUnshareViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        DocumentShare.objects.create(document=self.doc, shared_with=self.other)

    def test_owner_can_unshare(self):
        self.login(self.owner)
        self.client.post(
            reverse("core:document_unshare",
                    kwargs={"pk": self.doc.pk, "user_id": self.other.pk})
        )
        self.assertFalse(
            DocumentShare.objects.filter(document=self.doc, shared_with=self.other).exists()
        )

    def test_get_method_forbidden(self):
        self.login(self.owner)
        response = self.client.get(
            reverse("core:document_unshare",
                    kwargs={"pk": self.doc.pk, "user_id": self.other.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_other_user_cannot_unshare(self):
        self.login(self.other)
        response = self.client.post(
            reverse("core:document_unshare",
                    kwargs={"pk": self.doc.pk, "user_id": self.other.pk})
        )
        self.assertEqual(response.status_code, 403)


# ── Shared With Me ─────────────────────────────────────────────────────────────

class SharedWithMeViewTests(BaseTestCase):

    def test_shows_shared_docs(self):
        self.doc.visibility_status = Document.VIS_SHARED
        self.doc.save()
        DocumentShare.objects.create(document=self.doc, shared_with=self.other)
        self.login(self.other)
        response = self.client.get(reverse("core:shared_with_me"))
        self.assertContains(response, "Test Doc")

    def test_does_not_show_private_docs(self):
        DocumentShare.objects.create(document=self.doc, shared_with=self.other)
        self.login(self.other)
        response = self.client.get(reverse("core:shared_with_me"))
        self.assertNotContains(response, "Test Doc")

    def test_admin_gets_empty_list(self):
        self.login(self.admin)
        response = self.client.get(reverse("core:shared_with_me"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["documents"], [])


# ── Comments ───────────────────────────────────────────────────────────────────

class CommentAddViewTests(BaseTestCase):

    def test_owner_can_comment_on_own_doc(self):
        self.login(self.owner)
        self.client.post(
            reverse("core:comment_add", kwargs={"pk": self.doc.pk}),
            {"content": "My own comment"}
        )
        self.assertEqual(Comment.objects.filter(document=self.doc).count(), 1)

    def test_other_user_cannot_comment_on_private_doc(self):
        self.login(self.other)
        response = self.client.post(
            reverse("core:comment_add", kwargs={"pk": self.doc.pk}),
            {"content": "Sneaky comment"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.filter(document=self.doc).count(), 0)

    def test_comment_on_public_doc_sends_notification_to_owner(self):
        self.doc.visibility_status = Document.VIS_PUBLIC
        self.doc.save()
        self.login(self.other)
        self.client.post(
            reverse("core:comment_add", kwargs={"pk": self.doc.pk}),
            {"content": "Nice!"}
        )
        self.assertTrue(Notification.objects.filter(recipient=self.owner).exists())

    def test_no_notification_when_owner_comments_own_doc(self):
        self.doc.visibility_status = Document.VIS_PUBLIC
        self.doc.save()
        self.login(self.owner)
        self.client.post(
            reverse("core:comment_add", kwargs={"pk": self.doc.pk}),
            {"content": "Self comment"}
        )
        self.assertFalse(Notification.objects.filter(recipient=self.owner).exists())

    def test_get_method_forbidden(self):
        self.login(self.owner)
        response = self.client.get(
            reverse("core:comment_add", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_shared_user_can_comment(self):
        self.doc.visibility_status = Document.VIS_SHARED
        self.doc.save()
        DocumentShare.objects.create(document=self.doc, shared_with=self.other)
        self.login(self.other)
        self.client.post(
            reverse("core:comment_add", kwargs={"pk": self.doc.pk}),
            {"content": "Shared comment"}
        )
        self.assertEqual(Comment.objects.filter(document=self.doc).count(), 1)


class CommentDeleteViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.comment = Comment.objects.create(
            document=self.doc, author=self.other, content="A comment"
        )

    def test_comment_author_can_delete_own_comment(self):
    # other must be able to view the doc to delete their comment
        self.doc.visibility_status = Document.VIS_PUBLIC
        self.doc.save()
        self.login(self.other)
        self.client.post(
            reverse("core:comment_delete", kwargs={"cid": self.comment.pk})
        )
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())


    def test_doc_owner_can_delete_any_comment(self):
        self.login(self.owner)
        self.client.post(
            reverse("core:comment_delete", kwargs={"cid": self.comment.pk})
        )
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_admin_can_delete_any_comment(self):
        self.login(self.admin)
        self.client.post(
            reverse("core:comment_delete", kwargs={"cid": self.comment.pk})
        )
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_unrelated_user_cannot_delete_comment(self):
        third = User.objects.create_user(username="third", password="pass")
        self.doc.visibility_status = Document.VIS_PUBLIC
        self.doc.save()
        self.login(third)
        response = self.client.post(
            reverse("core:comment_delete", kwargs={"cid": self.comment.pk})
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_get_method_forbidden(self):
        self.login(self.owner)
        response = self.client.get(
            reverse("core:comment_delete", kwargs={"cid": self.comment.pk})
        )
        self.assertEqual(response.status_code, 403)


# ── Suggestions ────────────────────────────────────────────────────────────────

class SuggestionCreateViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.doc.visibility_status = Document.VIS_PUBLIC
        self.doc.save()

    def test_other_user_can_suggest_on_public_doc(self):
        self.login(self.other)
        self.client.post(
            reverse("core:suggestion_create", kwargs={"pk": self.doc.pk}),
            {"proposed_content": "My suggestion"}
        )
        self.assertEqual(EditSuggestion.objects.filter(document=self.doc).count(), 1)

    def test_owner_cannot_suggest_own_doc(self):
        self.login(self.owner)
        response = self.client.post(
            reverse("core:suggestion_create", kwargs={"pk": self.doc.pk}),
            {"proposed_content": "Owner suggestion"}
        )
        self.assertEqual(response.status_code, 403)

    def test_suggestion_sends_notification_to_owner(self):
        self.login(self.other)
        self.client.post(
            reverse("core:suggestion_create", kwargs={"pk": self.doc.pk}),
            {"proposed_content": "Suggest this"}
        )
        self.assertTrue(Notification.objects.filter(recipient=self.owner).exists())

    def test_private_doc_blocks_suggestion(self):
        self.doc.visibility_status = Document.VIS_PRIVATE
        self.doc.save()
        self.login(self.other)
        response = self.client.post(
            reverse("core:suggestion_create", kwargs={"pk": self.doc.pk}),
            {"proposed_content": "Sneak suggestion"}
        )
        self.assertEqual(response.status_code, 403)

    def test_get_prefills_form_with_current_content(self):
        self.login(self.other)
        response = self.client.get(
            reverse("core:suggestion_create", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.doc.content)


class SuggestionReviewActionTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.doc.visibility_status = Document.VIS_PUBLIC
        self.doc.save()
        self.suggestion = EditSuggestion.objects.create(
            document=self.doc,
            proposer=self.other,
            proposed_content="Better content",
        )

    def test_owner_can_accept_suggestion(self):
        self.login(self.owner)
        self.client.post(
            reverse("core:suggestion_review_action", kwargs={"sid": self.suggestion.pk}),
            {"action": "accept"}
        )
        self.doc.refresh_from_db()
        self.suggestion.refresh_from_db()
        self.assertEqual(self.doc.content, "Better content")
        self.assertEqual(self.suggestion.status, EditSuggestion.STATUS_ACCEPTED)

    def test_owner_can_reject_suggestion(self):
        self.login(self.owner)
        self.client.post(
            reverse("core:suggestion_review_action", kwargs={"sid": self.suggestion.pk}),
            {"action": "reject"}
        )
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, EditSuggestion.STATUS_REJECTED)

    def test_accept_sends_notification_to_proposer(self):
        self.login(self.owner)
        self.client.post(
            reverse("core:suggestion_review_action", kwargs={"sid": self.suggestion.pk}),
            {"action": "accept"}
        )
        self.assertTrue(Notification.objects.filter(recipient=self.other).exists())

    def test_reject_sends_notification_to_proposer(self):
        self.login(self.owner)
        self.client.post(
            reverse("core:suggestion_review_action", kwargs={"sid": self.suggestion.pk}),
            {"action": "reject"}
        )
        self.assertTrue(Notification.objects.filter(recipient=self.other).exists())

    def test_non_owner_cannot_review(self):
        self.login(self.other)
        response = self.client.post(
            reverse("core:suggestion_review_action", kwargs={"sid": self.suggestion.pk}),
            {"action": "accept"}
        )
        self.assertEqual(response.status_code, 403)

    def test_already_reviewed_suggestion_skips_action(self):
        self.suggestion.status = EditSuggestion.STATUS_ACCEPTED
        self.suggestion.save()
        self.login(self.owner)
        self.client.post(
            reverse("core:suggestion_review_action", kwargs={"sid": self.suggestion.pk}),
            {"action": "reject"}
        )
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, EditSuggestion.STATUS_ACCEPTED)

    def test_reviewed_at_is_set_on_accept(self):
        self.login(self.owner)
        self.client.post(
            reverse("core:suggestion_review_action", kwargs={"sid": self.suggestion.pk}),
            {"action": "accept"}
        )
        self.suggestion.refresh_from_db()
        self.assertIsNotNone(self.suggestion.reviewed_at)


# ── Attachments ────────────────────────────────────────────────────────────────

class AttachmentAddViewTests(BaseTestCase):

    def test_owner_can_upload_attachment(self):
        self.login(self.owner)
        file = SimpleUploadedFile("test.txt", b"file data")
        self.client.post(
            reverse("core:attachment_add", kwargs={"pk": self.doc.pk}),
            {"file": file}
        )
        self.assertEqual(
            DocumentAttachment.objects.filter(document=self.doc).count(), 1
        )

    def test_other_user_cannot_upload(self):
        self.login(self.other)
        file = SimpleUploadedFile("hack.txt", b"data")
        response = self.client.post(
            reverse("core:attachment_add", kwargs={"pk": self.doc.pk}),
            {"file": file}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            DocumentAttachment.objects.filter(document=self.doc).count(), 0
        )

    def test_get_method_forbidden(self):
        self.login(self.owner)
        response = self.client.get(
            reverse("core:attachment_add", kwargs={"pk": self.doc.pk})
        )
        self.assertEqual(response.status_code, 403)


class AttachmentDeleteViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.attachment = DocumentAttachment.objects.create(
            document=self.doc,
            uploaded_by=self.owner,
            file=SimpleUploadedFile("a.txt", b"data"),
            original_name="a.txt",
        )

    def test_owner_can_delete_attachment(self):
        self.login(self.owner)
        self.client.post(
            reverse("core:attachment_delete", kwargs={"aid": self.attachment.pk})
        )
        self.assertFalse(
            DocumentAttachment.objects.filter(pk=self.attachment.pk).exists()
        )

    def test_other_user_cannot_delete_attachment(self):
        self.login(self.other)
        response = self.client.post(
            reverse("core:attachment_delete", kwargs={"aid": self.attachment.pk})
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            DocumentAttachment.objects.filter(pk=self.attachment.pk).exists()
        )

    def test_admin_can_delete_attachment(self):
        self.login(self.admin)
        self.client.post(
            reverse("core:attachment_delete", kwargs={"aid": self.attachment.pk})
        )
        self.assertFalse(
            DocumentAttachment.objects.filter(pk=self.attachment.pk).exists()
        )

    def test_get_method_forbidden(self):
        self.login(self.owner)
        response = self.client.get(
            reverse("core:attachment_delete", kwargs={"aid": self.attachment.pk})
        )
        self.assertEqual(response.status_code, 403)


# ── Profile & Settings ─────────────────────────────────────────────────────────

class ProfileUpdateViewTests(BaseTestCase):

    def test_get_renders_profile_form(self):
        self.login(self.owner)
        response = self.client.get(reverse("core:profile_update"))
        self.assertEqual(response.status_code, 200)

    def test_post_updates_profile(self):
        self.login(self.owner)
        self.client.post(reverse("core:profile_update"), {
            "nickname": "Ally",
            "bio": "Writer",
        })
        self.owner.profile.refresh_from_db()
        self.assertEqual(self.owner.profile.nickname, "Ally")

    def test_requires_login(self):
        response = self.client.get(reverse("core:profile_update"))
        self.assertEqual(response.status_code, 302)


class SettingsViewTests(BaseTestCase):

    def test_get_renders_settings_form(self):
        self.login(self.owner)
        response = self.client.get(reverse("core:settings"))
        self.assertEqual(response.status_code, 200)

    def test_save_settings(self):
        self.login(self.owner)
        self.client.post(reverse("core:settings"), {
            "page_zoom": 120,
            "text_size": 20,
            "brightness": 80,
            "tts_enabled": False,
        })
        self.owner.profile.refresh_from_db()
        self.assertEqual(self.owner.profile.page_zoom, 120)

    def test_reset_defaults(self):
        self.owner.profile.page_zoom = 130
        self.owner.profile.save()
        self.login(self.owner)
        self.client.post(reverse("core:settings"), {"reset_defaults": "1"})
        self.owner.profile.refresh_from_db()
        self.assertEqual(self.owner.profile.page_zoom, 100)
        self.assertEqual(self.owner.profile.text_size, 16)
        self.assertEqual(self.owner.profile.brightness, 100)
        self.assertFalse(self.owner.profile.tts_enabled)


# ── Notifications ──────────────────────────────────────────────────────────────
class NotificationsViewTests(BaseTestCase):
    def test_shows_notifications(self):
        Notification.objects.create(recipient=self.owner, message="You have a note")
        self.login(self.owner)
        response = self.client.get(reverse("core:notifications"))
        self.assertContains(response, "You have a note")
    def test_mark_single_notification_as_read(self):
        notif = Notification.objects.create(
            recipient=self.owner, message="Read me", is_read=False
        )
        self.login(self.owner)
        self.client.post(reverse("core:mark_read", kwargs={"nid": notif.pk}))
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
    def test_mark_all_notifications_as_read(self):
        Notification.objects.create(recipient=self.owner, message="One", is_read=False)
        Notification.objects.create(recipient=self.owner, message="Two", is_read=False)
        self.login(self.owner)
        self.client.post(reverse("core:mark_all_read"))
        self.assertEqual(
            Notification.objects.filter(recipient=self.owner, is_read=False).count(), 0
        )
    def test_cannot_mark_another_users_notification(self):
        notif = Notification.objects.create(
            recipient=self.other, message="Private", is_read=False
        )
        self.login(self.owner)
        response = self.client.post(
            reverse("core:mark_read", kwargs={"nid": notif.pk})
        )
        self.assertEqual(response.status_code, 404)
    def test_requires_login(self):
        response = self.client.get(reverse("core:notifications"))
        self.assertEqual(response.status_code, 302)