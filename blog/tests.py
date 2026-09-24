import hashlib
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import patch

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase

from blog.models import Post


class CdnCorrectionMigrationTests(TestCase):
    def setUp(self):
        self.migration = import_module("blog.migrations.0013_correct_cdn_benchmark")
        self.editor = SimpleNamespace(connection=connection)
        self.author = get_user_model().objects.create_user(username="editor", email="editor@example.com")
        self.before = "Keep this introduction.\n\n" + self.migration.OLD_TEXT + "\n\nKeep this conclusion."
        self.after = self.before.replace(self.migration.OLD_TEXT, self.migration.NEW_TEXT)
        self.post = Post.objects.create(
            pk=self.migration.POST_ID,
            slug=self.migration.SLUG,
            author=self.author,
            title="Performance guide",
            content=self.before,
            status=Post.PUBLISHED,
        )
        for name, body in [("OLD_SHA256", self.before), ("NEW_SHA256", self.after)]:
            patcher = patch.object(self.migration, name, hashlib.sha256(body.encode()).hexdigest())
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_reversible_correction_preserves_other_copy_and_publication(self):
        created, modified = self.post.created, self.post.modified
        self.migration.forwards(apps, self.editor)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, self.after)
        self.assertEqual(self.post.created, created)
        self.assertEqual(self.post.status, Post.PUBLISHED)
        self.assertGreater(self.post.modified, modified)

        self.migration.backwards(apps, self.editor)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, self.before)
        self.assertEqual(self.post.created, created)

    def test_changed_article_is_not_overwritten_in_either_direction(self):
        for direction, body in [("forwards", self.before), ("backwards", self.after)]:
            with self.subTest(direction=direction):
                changed = body + "\nAn editor's newer paragraph."
                Post.objects.filter(pk=self.post.pk).update(content=changed)
                with self.assertRaisesRegex(RuntimeError, "Article changed"):
                    getattr(self.migration, direction)(apps, self.editor)
                self.post.refresh_from_db()
                self.assertEqual(self.post.content, changed)

    def test_wrong_row_identity_is_not_changed(self):
        Post.objects.filter(pk=self.post.pk).update(slug="another-article")
        with self.assertRaisesRegex(RuntimeError, "target does not match"):
            self.migration.forwards(apps, self.editor)

    def test_missing_production_row_is_safe_for_fresh_installs(self):
        self.post.delete()
        self.migration.forwards(apps, self.editor)
        self.migration.backwards(apps, self.editor)
        self.assertEqual(Post.objects.count(), 0)

    def test_reapplication_does_not_refresh_modified_again(self):
        self.migration.forwards(apps, self.editor)
        self.post.refresh_from_db()
        modified = self.post.modified
        self.migration.forwards(apps, self.editor)
        self.post.refresh_from_db()
        self.assertEqual(self.post.modified, modified)
