from unittest.mock import patch

from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import reverse

from blog.content import all_posts, published_posts, read_post
from blog.feeds import BlogFeed
from blog.models import Comment, Post as ArchivedPost, Tag
from blog.testing import make_post
from blog.views import PostDetailView
from builtwithdjango.sitemaps import BlogSitemap


class RepositoryPostTests(SimpleTestCase):
    def test_real_content_inventory_is_valid_and_has_no_db_dependency(self):
        posts = all_posts()
        self.assertGreaterEqual(len(posts), 28)
        self.assertEqual(len({p.id for p in posts}), len(posts))
        self.assertTrue(all(p.get_absolute_url() == f"/blog/{p.slug}" for p in posts))

    def test_published_surfaces_exclude_drafts_and_sort_by_original_date(self):
        old = make_post(self, slug="old", created="2020-01-01T00:00:00Z")
        new = make_post(self, slug="new", created="2021-01-01T00:00:00Z", type="ARTICLE")
        draft = make_post(self, slug="draft", status="DR")
        self.assertEqual(published_posts(), [new, old])
        self.assertEqual(published_posts("TUTORIAL"), [old])
        self.assertEqual(BlogFeed().items(), [new, old])
        self.assertEqual(BlogFeed().item_pubdate(old), old.created)
        self.assertEqual(BlogSitemap().items(), [new, old])
        self.assertEqual(BlogSitemap().lastmod(old), old.modified)
        with patch("blog.views.capture"):
            for slug in (draft.slug, "unknown", "../old"):
                response = self.client.get(f"/blog/{slug}")
                self.assertEqual(response.status_code, 404)

    def test_post_view_keeps_markdown_metadata_and_analytics_id(self):
        post = make_post(self, id=152)
        request = RequestFactory().get(post.get_absolute_url())
        with patch("blog.views.capture") as capture:
            response = PostDetailView.as_view()(request, slug=post.slug)
        self.assertEqual(response.context_data["object"], post)
        self.assertEqual(capture.call_args.kwargs["properties"]["post_id"], 152)

    def test_missing_directory_duplicate_id_and_bad_metadata_fail_closed(self):
        post = make_post(self)
        make_post(self, slug="duplicate", id=post.id)
        with self.assertRaises(ImproperlyConfigured):
            all_posts()
        with override_settings(BLOG_CONTENT_DIR=self.blog_directory / "missing"):
            with self.assertRaises(ImproperlyConfigured):
                all_posts()
        path = self.blog_directory / "test-guide.md"
        original = path.read_text()
        for text in (
            "no front matter",
            original.replace("status: PB", "status: TYPO"),
            original.replace("id: 1", "id: false"),
            original.replace("slug: test-guide", "slug: ../../secret"),
        ):
            path.write_text(text)
            with self.assertRaises(ImproperlyConfigured):
                read_post(path)

    def test_frontmatter_delimiter_in_body_is_preserved(self):
        post = make_post(self, content="# Body\n\n---\n\n```python\nprint('hi')\n```\n")
        self.assertEqual(post.content, "# Body\n\n---\n\n```python\nprint('hi')\n```\n")

    def test_crlf_front_matter_preserves_body_line_endings(self):
        post = make_post(self, content="First line\nSecond line\n")
        path = self.blog_directory / (post.slug + ".md")
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(read_post(path).content, "First line\r\nSecond line\r\n")

    def test_file_edits_reload_in_the_same_process(self):
        original = make_post(self)
        self.assertEqual(all_posts(), [original])
        updated = make_post(self, id=original.id, content="Edited **Markdown** body.")
        self.assertEqual(all_posts(), [updated])
        self.assertNotEqual(original.content, updated.content)

    def test_legacy_admin_cannot_publish_or_delete(self):
        request = RequestFactory().get("/")
        for model in (ArchivedPost, Tag, Comment):
            model_admin = admin.site._registry[model]
            self.assertFalse(model_admin.has_add_permission(request))
            self.assertFalse(model_admin.has_change_permission(request))
            self.assertFalse(model_admin.has_delete_permission(request))
