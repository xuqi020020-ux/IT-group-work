from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Document, DocumentShare, EditSuggestion, Comment
from .views import can_view_document, can_comment


# ---------------------------------------------------------------------------
# Helper function: can_view_document
# ---------------------------------------------------------------------------

class CanViewDocumentTests(TestCase):
    def setUp(self):
        self.owner   = User.objects.create_user(username="owner",   password="pass")
        self.other   = User.objects.create_user(username="other",   password="pass")
        self.admin   = User.objects.create_user(username="admin",   password="pass", is_staff=True)
        self.shared_user = User.objects.create_user(username="shared", password="pass")

    def _doc(self, visibility):
        return Document.objects.create(owner=self.owner, title="T", visibility_status=visibility)

    def test_admin_can_view_all_visibility_statuses(self):
        for vis in [Document.VIS_PRIVATE, Document.VIS_SHARED,
                    Document.VIS_PUBLIC, Document.VIS_MODERATED]:
            with self.subTest(visibility=vis):
                self.assertTrue(can_view_document(self.admin, self._doc(vis)))

    def test_owner_can_view_own_doc_regardless_of_status(self):
        # Owner must be able to view even moderated documents
        for vis in [Document.VIS_PRIVATE, Document.VIS_SHARED,
                    Document.VIS_PUBLIC, Document.VIS_MODERATED]:
            with self.subTest(visibility=vis):
                self.assertTrue(can_view_document(self.owner, self._doc(vis)))

    def test_moderated_doc_hidden_from_non_owner(self):
        self.assertFalse(can_view_document(self.other, self._doc(Document.VIS_MODERATED)))

    def test_public_doc_visible_to_any_user(self):
        self.assertTrue(can_view_document(self.other, self._doc(Document.VIS_PUBLIC)))

    def test_private_doc_hidden_from_non_owner(self):
        self.assertFalse(can_view_document(self.other, self._doc(Document.VIS_PRIVATE)))

    def test_shared_doc_visible_to_explicitly_shared_user(self):
        doc = self._doc(Document.VIS_SHARED)
        DocumentShare.objects.create(document=doc, shared_with=self.shared_user)
        self.assertTrue(can_view_document(self.shared_user, doc))

    def test_shared_doc_hidden_from_user_not_in_share_list(self):
        doc = self._doc(Document.VIS_SHARED)
        self.assertFalse(can_view_document(self.other, doc))


# ---------------------------------------------------------------------------
# Helper function: can_comment
# ---------------------------------------------------------------------------

class CanCommentTests(TestCase):
    def setUp(self):
        self.owner  = User.objects.create_user(username="owner",  password="pass")
        self.other  = User.objects.create_user(username="other",  password="pass")
        self.admin  = User.objects.create_user(username="admin",  password="pass", is_staff=True)
        self.shared = User.objects.create_user(username="shared", password="pass")

    def test_owner_can_comment_on_private_doc(self):
        doc = Document.objects.create(owner=self.owner, title="T", visibility_status=Document.VIS_PRIVATE)
        self.assertTrue(can_comment(self.owner, doc))

    def test_admin_can_comment_on_any_doc(self):
        doc = Document.objects.create(owner=self.owner, title="T", visibility_status=Document.VIS_PRIVATE)
        self.assertTrue(can_comment(self.admin, doc))

    def test_other_user_can_comment_on_public_doc(self):
        doc = Document.objects.create(owner=self.owner, title="T", visibility_status=Document.VIS_PUBLIC)
        self.assertTrue(can_comment(self.other, doc))

    def test_shared_user_can_comment_on_shared_doc(self):
        doc = Document.objects.create(owner=self.owner, title="T", visibility_status=Document.VIS_SHARED)
        DocumentShare.objects.create(document=doc, shared_with=self.shared)
        self.assertTrue(can_comment(self.shared, doc))

    def test_other_user_blocked_from_commenting_on_private_doc(self):
        doc = Document.objects.create(owner=self.owner, title="T", visibility_status=Document.VIS_PRIVATE)
        self.assertFalse(can_comment(self.other, doc))

    def test_other_user_blocked_from_commenting_on_moderated_doc(self):
        # Moderated docs are invisible to non-owners, so commenting must be blocked too
        doc = Document.objects.create(owner=self.owner, title="T", visibility_status=Document.VIS_MODERATED)
        self.assertFalse(can_comment(self.other, doc))

    def test_unshared_user_cannot_comment_on_shared_doc(self):
        doc = Document.objects.create(owner=self.owner, title="T", visibility_status=Document.VIS_SHARED)
        self.assertFalse(can_comment(self.other, doc))


# ---------------------------------------------------------------------------
# Model __str__ methods
# ---------------------------------------------------------------------------

class ModelStrTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="pass")
        self.doc  = Document.objects.create(owner=self.user, title="My Doc")

    def test_document_str_returns_title(self):
        self.assertEqual(str(self.doc), "My Doc")

    def test_document_share_str_contains_ids(self):
        other = User.objects.create_user(username="v", password="pass")
        share = DocumentShare.objects.create(document=self.doc, shared_with=other)
        # Format is "<doc_id> -> <user_id>"
        self.assertIn(str(self.doc.id), str(share))
        self.assertIn(str(other.id), str(share))

    def test_edit_suggestion_str_contains_doc_id(self):
        proposer = User.objects.create_user(username="p", password="pass")
        sug = EditSuggestion.objects.create(
            document=self.doc, proposer=proposer, proposed_content="abc"
        )
        self.assertIn(str(self.doc.id), str(sug))

    def test_comment_str_contains_doc_id(self):
        c = Comment.objects.create(document=self.doc, author=self.user, content="hello")
        self.assertIn(str(self.doc.id), str(c))


# ---------------------------------------------------------------------------
# Dashboard view
# ---------------------------------------------------------------------------

class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user   = User.objects.create_user(username="u",     password="pass")
        self.other  = User.objects.create_user(username="other", password="pass")
        self.admin  = User.objects.create_user(username="admin", password="pass", is_staff=True)

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_user_sees_their_own_documents(self):
        Document.objects.create(owner=self.user, title="My Note", visibility_status=Document.VIS_PRIVATE)
        self.client.login(username="u", password="pass")
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Note")

    def test_user_does_not_see_others_private_documents(self):
        Document.objects.create(owner=self.other, title="Secret", visibility_status=Document.VIS_PRIVATE)
        self.client.login(username="u", password="pass")
        response = self.client.get(reverse("core:dashboard"))
        self.assertNotContains(response, "Secret")

    def test_user_sees_public_documents_from_others(self):
        Document.objects.create(owner=self.other, title="Public Note", visibility_status=Document.VIS_PUBLIC)
        self.client.login(username="u", password="pass")
        response = self.client.get(reverse("core:dashboard"))
        self.assertContains(response, "Public Note")

    def test_user_does_not_see_moderated_documents(self):
        Document.objects.create(owner=self.other, title="Moderated", visibility_status=Document.VIS_MODERATED)
        self.client.login(username="u", password="pass")
        response = self.client.get(reverse("core:dashboard"))
        self.assertNotContains(response, "Moderated")

    def test_admin_sees_moderated_documents(self):
        Document.objects.create(owner=self.user, title="ModDoc", visibility_status=Document.VIS_MODERATED)
        self.client.login(username="admin", password="pass")
        response = self.client.get(reverse("core:dashboard"))
        self.assertContains(response, "ModDoc")

    def test_search_filters_results_by_title(self):
        Document.objects.create(owner=self.user, title="AlphaNote", visibility_status=Document.VIS_PUBLIC)
        Document.objects.create(owner=self.user, title="BetaNote",  visibility_status=Document.VIS_PUBLIC)
        self.client.login(username="u", password="pass")
        response = self.client.get(reverse("core:dashboard") + "?q=Alpha")
        self.assertContains(response, "AlphaNote")
        self.assertNotContains(response, "BetaNote")


# ---------------------------------------------------------------------------
# Document detail view
# ---------------------------------------------------------------------------

class DocumentDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner  = User.objects.create_user(username="owner",  password="pass")
        self.other  = User.objects.create_user(username="other",  password="pass")
        self.shared = User.objects.create_user(username="shared", password="pass")

    def test_owner_can_view_private_document(self):
        doc = Document.objects.create(owner=self.owner, title="Priv", visibility_status=Document.VIS_PRIVATE)
        self.client.login(username="owner", password="pass")
        response = self.client.get(reverse("core:document_detail", args=[doc.pk]))
        self.assertEqual(response.status_code, 200)

    def test_non_owner_cannot_view_private_document(self):
        doc = Document.objects.create(owner=self.owner, title="Priv", visibility_status=Document.VIS_PRIVATE)
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("core:document_detail", args=[doc.pk]))
        self.assertEqual(response.status_code, 403)

    def test_any_user_can_view_public_document(self):
        doc = Document.objects.create(owner=self.owner, title="Pub", visibility_status=Document.VIS_PUBLIC)
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("core:document_detail", args=[doc.pk]))
        self.assertEqual(response.status_code, 200)

    def test_shared_user_can_view_shared_document(self):
        doc = Document.objects.create(owner=self.owner, title="Shared", visibility_status=Document.VIS_SHARED)
        DocumentShare.objects.create(document=doc, shared_with=self.shared)
        self.client.login(username="shared", password="pass")
        response = self.client.get(reverse("core:document_detail", args=[doc.pk]))
        self.assertEqual(response.status_code, 200)

    def test_non_shared_user_cannot_view_shared_document(self):
        doc = Document.objects.create(owner=self.owner, title="Shared", visibility_status=Document.VIS_SHARED)
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("core:document_detail", args=[doc.pk]))
        self.assertEqual(response.status_code, 403)

    def test_non_owner_cannot_view_moderated_document(self):
        doc = Document.objects.create(owner=self.owner, title="Mod", visibility_status=Document.VIS_MODERATED)
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("core:document_detail", args=[doc.pk]))
        self.assertEqual(response.status_code, 403)


# ---------------------------------------------------------------------------
# Document create / edit / delete views
# ---------------------------------------------------------------------------

class DocumentCRUDViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner  = User.objects.create_user(username="owner",  password="pass")
        self.other  = User.objects.create_user(username="other",  password="pass")
        self.admin  = User.objects.create_user(username="admin",  password="pass", is_staff=True)

    def test_create_document_sets_current_user_as_owner(self):
        self.client.login(username="owner", password="pass")
        self.client.post(reverse("core:document_create"), {
            "title": "New Doc",
            "content": "Content",
            "visibility_status": Document.VIS_PRIVATE,
        })
        doc = Document.objects.get(title="New Doc")
        self.assertEqual(doc.owner, self.owner)

    def test_owner_can_edit_document(self):
        doc = Document.objects.create(owner=self.owner, title="Old", visibility_status=Document.VIS_PRIVATE)
        self.client.login(username="owner", password="pass")
        self.client.post(reverse("core:document_edit", args=[doc.pk]), {
            "title": "New Title",
            "content": "",
            "visibility_status": Document.VIS_PRIVATE,
        })
        doc.refresh_from_db()
        self.assertEqual(doc.title, "New Title")

    def test_non_owner_cannot_edit_document(self):
        doc = Document.objects.create(owner=self.owner, title="Doc", visibility_status=Document.VIS_PRIVATE)
        self.client.login(username="other", password="pass")
        response = self.client.post(reverse("core:document_edit", args=[doc.pk]), {
            "title": "Hacked",
            "content": "",
            "visibility_status": Document.VIS_PRIVATE,
        })
        self.assertEqual(response.status_code, 403)
        doc.refresh_from_db()
        self.assertEqual(doc.title, "Doc")  # unchanged

    def test_admin_can_edit_any_document(self):
        doc = Document.objects.create(owner=self.owner, title="Doc", visibility_status=Document.VIS_PRIVATE)
        self.client.login(username="admin", password="pass")
        self.client.post(reverse("core:document_edit", args=[doc.pk]), {
            "title": "Admin Edit",
            "content": "",
            "visibility_status": Document.VIS_PRIVATE,
        })
        doc.refresh_from_db()
        self.assertEqual(doc.title, "Admin Edit")

    def test_owner_can_delete_document(self):
        doc = Document.objects.create(owner=self.owner, title="Bye", visibility_status=Document.VIS_PRIVATE)
        self.client.login(username="owner", password="pass")
        self.client.post(reverse("core:document_delete", args=[doc.pk]))
        self.assertFalse(Document.objects.filter(pk=doc.pk).exists())

    def test_non_owner_cannot_delete_document(self):
        doc = Document.objects.create(owner=self.owner, title="Protected", visibility_status=Document.VIS_PRIVATE)
        self.client.login(username="other", password="pass")
        response = self.client.post(reverse("core:document_delete", args=[doc.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Document.objects.filter(pk=doc.pk).exists())


# ---------------------------------------------------------------------------
# Edit suggestion workflow
# ---------------------------------------------------------------------------

class SuggestionTests(TestCase):
    def setUp(self):
        self.client   = Client()
        self.owner    = User.objects.create_user(username="owner",    password="pass")
        self.proposer = User.objects.create_user(username="proposer", password="pass")
        self.stranger = User.objects.create_user(username="stranger", password="pass")

    def test_proposer_can_submit_suggestion_on_public_doc(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", content="Original",
            visibility_status=Document.VIS_PUBLIC,
        )
        self.client.login(username="proposer", password="pass")
        self.client.post(reverse("core:suggestion_create", args=[doc.pk]), {
            "proposed_content": "Improved",
        })
        self.assertEqual(
            EditSuggestion.objects.filter(document=doc, proposer=self.proposer).count(), 1
        )

    def test_owner_cannot_suggest_on_own_document(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", visibility_status=Document.VIS_PUBLIC
        )
        self.client.login(username="owner", password="pass")
        response = self.client.post(reverse("core:suggestion_create", args=[doc.pk]), {
            "proposed_content": "Edit",
        })
        self.assertEqual(response.status_code, 403)

    def test_suggestion_blocked_on_private_document(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", visibility_status=Document.VIS_PRIVATE
        )
        self.client.login(username="proposer", password="pass")
        response = self.client.post(reverse("core:suggestion_create", args=[doc.pk]), {
            "proposed_content": "Edit",
        })
        self.assertEqual(response.status_code, 403)

    def test_accepting_suggestion_updates_document_content(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", content="Original",
            visibility_status=Document.VIS_PUBLIC,
        )
        sug = EditSuggestion.objects.create(
            document=doc, proposer=self.proposer, proposed_content="Improved"
        )
        self.client.login(username="owner", password="pass")
        self.client.post(reverse("core:suggestion_review_action", args=[sug.pk]), {"action": "accept"})
        doc.refresh_from_db()
        sug.refresh_from_db()
        self.assertEqual(doc.content, "Improved")
        self.assertEqual(sug.status, EditSuggestion.STATUS_ACCEPTED)
        self.assertIsNotNone(sug.reviewed_at)

    def test_rejecting_suggestion_leaves_document_content_unchanged(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", content="Original",
            visibility_status=Document.VIS_PUBLIC,
        )
        sug = EditSuggestion.objects.create(
            document=doc, proposer=self.proposer, proposed_content="Improved"
        )
        self.client.login(username="owner", password="pass")
        self.client.post(reverse("core:suggestion_review_action", args=[sug.pk]), {"action": "reject"})
        doc.refresh_from_db()
        sug.refresh_from_db()
        self.assertEqual(doc.content, "Original")
        self.assertEqual(sug.status, EditSuggestion.STATUS_REJECTED)

    def test_non_owner_cannot_review_suggestion(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", content="X",
            visibility_status=Document.VIS_PUBLIC,
        )
        sug = EditSuggestion.objects.create(
            document=doc, proposer=self.proposer, proposed_content="Y"
        )
        self.client.login(username="stranger", password="pass")
        response = self.client.post(
            reverse("core:suggestion_review_action", args=[sug.pk]), {"action": "accept"}
        )
        self.assertEqual(response.status_code, 403)

    def test_already_reviewed_suggestion_is_not_reprocessed(self):
        # A suggestion that was already rejected must not be accepted again
        doc = Document.objects.create(
            owner=self.owner, title="Doc", content="Original",
            visibility_status=Document.VIS_PUBLIC,
        )
        sug = EditSuggestion.objects.create(
            document=doc, proposer=self.proposer, proposed_content="Improved",
            status=EditSuggestion.STATUS_REJECTED,
        )
        self.client.login(username="owner", password="pass")
        self.client.post(reverse("core:suggestion_review_action", args=[sug.pk]), {"action": "accept"})
        doc.refresh_from_db()
        self.assertEqual(doc.content, "Original")


# ---------------------------------------------------------------------------
# Comment add / delete views
# ---------------------------------------------------------------------------

class CommentTests(TestCase):
    def setUp(self):
        self.client   = Client()
        self.owner    = User.objects.create_user(username="owner",    password="pass")
        self.viewer   = User.objects.create_user(username="viewer",   password="pass")
        self.stranger = User.objects.create_user(username="stranger", password="pass")

    def test_viewer_can_comment_on_public_document(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", visibility_status=Document.VIS_PUBLIC
        )
        self.client.login(username="viewer", password="pass")
        self.client.post(reverse("core:comment_add", args=[doc.pk]), {"content": "Nice!"})
        self.assertEqual(Comment.objects.filter(document=doc, author=self.viewer).count(), 1)

    def test_comment_blocked_on_private_document_for_non_owner(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", visibility_status=Document.VIS_PRIVATE
        )
        self.client.login(username="viewer", password="pass")
        response = self.client.post(reverse("core:comment_add", args=[doc.pk]), {"content": "Hi"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.filter(document=doc).count(), 0)

    def test_owner_can_comment_on_own_private_document(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", visibility_status=Document.VIS_PRIVATE
        )
        self.client.login(username="owner", password="pass")
        self.client.post(reverse("core:comment_add", args=[doc.pk]), {"content": "My note"})
        self.assertEqual(Comment.objects.filter(document=doc, author=self.owner).count(), 1)

    def test_comment_author_can_delete_own_comment(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", visibility_status=Document.VIS_PUBLIC
        )
        comment = Comment.objects.create(document=doc, author=self.viewer, content="Hi")
        self.client.login(username="viewer", password="pass")
        self.client.post(reverse("core:comment_delete", args=[comment.pk]))
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_document_owner_can_delete_any_comment_on_their_doc(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", visibility_status=Document.VIS_PUBLIC
        )
        comment = Comment.objects.create(document=doc, author=self.viewer, content="Hi")
        self.client.login(username="owner", password="pass")
        self.client.post(reverse("core:comment_delete", args=[comment.pk]))
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_unrelated_user_cannot_delete_others_comment(self):
        doc = Document.objects.create(
            owner=self.owner, title="Doc", visibility_status=Document.VIS_PUBLIC
        )
        comment = Comment.objects.create(document=doc, author=self.viewer, content="Hi")
        self.client.login(username="stranger", password="pass")
        response = self.client.post(reverse("core:comment_delete", args=[comment.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())
