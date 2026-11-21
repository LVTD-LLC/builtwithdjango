import importlib
import json
from base64 import b64decode
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone
from webpack_boilerplate import utils as webpack_utils

from .models import Like, Project, ProjectTitleAlias
from .views import ProjectListView


class ProjectOwnershipTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.test_files = TemporaryDirectory()
        self.addCleanup(self.test_files.cleanup)

        manifest_path = Path(self.test_files.name) / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "entrypoints": {
                        "hotwire": {
                            "assets": {
                                "js": ["/static/js/hotwire.js"],
                                "css": ["/static/css/hotwire.css"],
                            },
                        },
                    },
                    "css/hotwire.css": "/static/css/hotwire.css",
                    "js/hotwire.js": "/static/js/hotwire.js",
                },
            ),
            encoding="utf-8",
        )

        webpack_utils._loaders.clear()
        self.file_settings = override_settings(
            MEDIA_ROOT=str(Path(self.test_files.name) / "media"),
            WEBPACK_LOADER={
                "CACHE": False,
                "MANIFEST_FILE": str(manifest_path),
            },
        )
        self.file_settings.enable()
        self.addCleanup(self.file_settings.disable)
        self.addCleanup(webpack_utils._loaders.clear)

        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="password")
        self.other_user = User.objects.create_user(
            username="other-user",
            email="other@example.com",
            password="password",
        )
        self.project = Project.objects.create(
            title="Owner Project",
            url="https://owner-project.example.com",
            short_description="The original description.",
            logged_in_maker=self.owner,
            published=True,
        )

    def test_anonymous_users_must_sign_in_before_submitting_a_project(self):
        response = self.client.post(
            reverse("submit_project"),
            {
                "title": "Anonymous Project",
                "url": "https://anonymous-project.example.com",
                "short_description": "This should not be created.",
            },
        )

        self.assertRedirects(
            response,
            f"{reverse('account_login')}?next={reverse('submit_project')}",
            fetch_redirect_response=False,
        )
        self.assertFalse(Project.objects.filter(title="Anonymous Project").exists())

    def test_anonymous_users_must_sign_in_before_editing_a_project(self):
        update_url = reverse("project_update", kwargs={"slug": self.project.slug})

        response = self.client.get(update_url)

        self.assertRedirects(
            response,
            f"{reverse('account_login')}?next={update_url}",
            fetch_redirect_response=False,
        )

    def test_authenticated_submitter_becomes_project_owner(self):
        self.client.force_login(self.owner)

        with patch("projects.views.async_task"):
            response = self.client.post(
                reverse("submit_project"),
                {
                    "url": "https://submitted-project.example.com",
                },
            )

        self.assertRedirects(response, reverse("projects"), fetch_redirect_response=False)
        self.assertEqual(Project.objects.get(url="https://submitted-project.example.com").logged_in_maker, self.owner)

    def test_owner_can_update_project_metadata_and_screenshot(self):
        self.client.force_login(self.owner)
        update_url = reverse("project_update", kwargs={"slug": self.project.slug})
        edit_response = self.client.get(update_url)
        screenshot = SimpleUploadedFile(
            "updated-screenshot.gif",
            b64decode("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="),
            content_type="image/gif",
        )

        response = self.client.post(
            update_url,
            {
                "title": "Updated Owner Project",
                "url": "https://updated-owner-project.example.com",
                "short_description": "An updated description.",
                "homepage_screenshot": screenshot,
            },
        )

        self.project.refresh_from_db()
        self.assertContains(edit_response, 'name="homepage_screenshot"', html=False)
        self.assertRedirects(response, self.project.get_absolute_url(), fetch_redirect_response=False)
        self.assertEqual(self.project.title, "Updated Owner Project")
        self.assertEqual(self.project.url, "https://updated-owner-project.example.com")
        self.assertEqual(self.project.short_description, "An updated description.")
        self.assertTrue(self.project.homepage_screenshot.name.endswith("updated-screenshot.gif"))

    def test_owner_url_update_clears_stale_enrichment_without_queuing_refreshes(self):
        self.project.page_title = "Old page title"
        self.project.page_content_markdown = "Old page content"
        self.project.content_summary = "Old analysis"
        self.project.might_be_spam = True
        self.project.homepage_screenshot = "website_homepage_screenshot/old.png"
        self.project.save()
        self.client.force_login(self.owner)

        with patch("projects.views.async_task") as mock_async_task:
            response = self.client.post(
                reverse("project_update", kwargs={"slug": self.project.slug}),
                {
                    "title": self.project.title,
                    "url": "https://new-owner-project.example.com",
                    "short_description": self.project.short_description,
                },
            )

        self.project.refresh_from_db()
        self.assertRedirects(response, self.project.get_absolute_url(), fetch_redirect_response=False)
        self.assertEqual(self.project.page_title, "")
        self.assertEqual(self.project.page_content_markdown, "")
        self.assertEqual(self.project.content_summary, "")
        self.assertFalse(self.project.might_be_spam)
        self.assertFalse(self.project.homepage_screenshot)
        mock_async_task.assert_not_called()

    def test_owner_title_update_preserves_existing_project_slug(self):
        original_slug = self.project.slug
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("project_update", kwargs={"slug": original_slug}),
            {
                "title": "Renamed Owner Project",
                "url": self.project.url,
                "short_description": self.project.short_description,
            },
        )

        self.project.refresh_from_db()
        self.assertRedirects(
            response, reverse("project", kwargs={"slug": original_slug}), fetch_redirect_response=False
        )
        self.assertEqual(self.project.title, "Renamed Owner Project")
        self.assertEqual(self.project.slug, original_slug)
        self.assertTrue(ProjectTitleAlias.objects.filter(project=self.project, title="Owner Project").exists())
        self.assertEqual(self.client.get(reverse("project", kwargs={"slug": original_slug})).status_code, 200)

    def test_non_owner_cannot_view_or_update_project(self):
        self.client.force_login(self.other_user)
        update_url = reverse("project_update", kwargs={"slug": self.project.slug})

        get_response = self.client.get(update_url)
        post_response = self.client.post(
            update_url,
            {
                "title": "Stolen Project",
                "url": "https://stolen-project.example.com",
                "short_description": "Changed by someone else.",
            },
        )

        self.project.refresh_from_db()
        self.assertEqual(get_response.status_code, 403)
        self.assertEqual(post_response.status_code, 403)
        self.assertEqual(self.project.title, "Owner Project")
        self.assertEqual(self.project.url, "https://owner-project.example.com")

    def test_matching_submitter_email_does_not_claim_an_unlinked_project(self):
        unlinked_project = Project.objects.create(
            title="Legacy Project",
            url="https://legacy-project.example.com",
            short_description="Submitted before account ownership was linked.",
            user_email=self.owner.email,
            published=True,
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse("project_update", kwargs={"slug": unlinked_project.slug}))

        self.assertEqual(response.status_code, 403)

    def test_curated_reading_links_match_the_project_repository(self):
        for slug, repository, anchor in [
            ("pinry", "https://github.com/pinry/pinry", "read-pinry-permissions"),
            ("baby-buddy", "https://github.com/babybuddy/babybuddy", "read-baby-buddy-notes"),
        ]:
            with self.subTest(slug=slug):
                self.project.slug = slug
                self.project.github_url = repository
                self.project.save()
                url = reverse("project", kwargs={"slug": slug})
                response = self.client.get(url)
                self.assertContains(response, f'href="/projects/#{anchor}"')
                self.assertContains(response, 'data-analytics-cta="open project reading path"')
                self.assertContains(response, "Learn from this codebase")
                self.assertContains(response, repository + "?ref=testserver")

                self.project.github_url = "https://github.com/unrelated/project"
                self.project.save()
                self.assertNotContains(self.client.get(url), "Learn from this codebase")

    def test_curated_reading_link_is_absent_from_private_preview(self):
        self.project.slug = "pinry"
        self.project.github_url = "https://github.com/pinry/pinry"
        self.project.published = False
        self.project.save()
        url = reverse("project", kwargs={"slug": "pinry"})
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.owner)
        self.assertNotContains(self.client.get(url), "Learn from this codebase")

    def test_curated_reading_dates_preserve_newer_project_revisions(self):
        from datetime import datetime, timezone as dt_timezone

        from builtwithdjango.sitemaps import sitemaps

        self.project.slug = "pinry"
        self.project.github_url = "https://github.com/pinry/pinry"
        self.project.save()
        old_date = datetime(2026, 10, 1, tzinfo=dt_timezone.utc)
        Project.objects.filter(pk=self.project.pk).update(updated_date=old_date)
        self.project.refresh_from_db()
        self.assertEqual(
            sitemaps["projects"].lastmod(self.project), datetime(2026, 11, 17, tzinfo=dt_timezone.utc)
        )
        Project.objects.create(
            title="Another public project", url="https://another.example.com",
            short_description="No curated reading path.", published=True, active=True,
        )
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)
        newer_date = datetime(2026, 11, 20, tzinfo=dt_timezone.utc)
        Project.objects.filter(pk=self.project.pk).update(updated_date=newer_date)
        self.project.refresh_from_db()
        self.assertEqual(sitemaps["projects"].lastmod(self.project), newer_date)
        self.project.github_url = "https://github.com/another/repository"
        self.assertEqual(sitemaps["projects"].lastmod(self.project), newer_date)


class ProjectTestCase(TestCase):
    def setUp(self):
        Project.objects.create(
            title="Test Site 1",
            url="https://test.com",
            short_description="This is fake test website",
            user_email="test1@test.com",
        )
        Project.objects.create(
            title="Example Site 1",
            url="https://example.com",
            short_description="This is fake example website",
            user_email="example1@example.com",
            published=True,
        )

    def test_Projects_have_email(self):
        """Projects that can speak are correctly identified"""
        test = Project.objects.get(title="Test Site 1")
        example = Project.objects.get(title="Example Site 1")
        self.assertEqual(test.user_email, "test1@test.com")
        self.assertEqual(example.user_email, "example1@example.com")

    def test_Projects_is_published(self):
        """Projects that can speak are correctly identified"""
        test = Project.objects.get(title="Test Site 1")
        example = Project.objects.get(title="Example Site 1")
        self.assertEqual(test.published, False)
        self.assertEqual(example.published, True)

class ProjectModelServiceTests(TestCase):
    def test_check_project_is_active_updates_active_flag_from_http_status(self):
        project = Project.objects.create(
            title="Active Project",
            url="https://active.example.com",
            short_description="A project.",
        )

        with patch("projects.models.requests.get", return_value=Mock(status_code=200)) as get:
            self.assertTrue(project.check_project_is_active())

        self.assertTrue(project.active)
        get.assert_called_once_with(project.url, timeout=7)

    def test_check_project_is_active_handles_request_errors(self):
        project = Project.objects.create(
            title="Inactive Project",
            url="https://inactive.example.com",
            short_description="A project.",
        )

        with patch("projects.models.requests.get", side_effect=requests.Timeout):
            self.assertFalse(project.check_project_is_active())

        self.assertFalse(project.active)

class ProjectListViewTests(TestCase):
    def test_project_list_filters_public_active_non_spam_projects(self):
        visible = Project.objects.create(
            title="Visible Project",
            url="https://visible.example.com",
            short_description="Visible.",
            published=True,
            active=True,
            might_be_spam=False,
        )
        Project.objects.create(
            title="Draft Project",
            url="https://draft.example.com",
            short_description="Draft.",
            published=False,
            active=True,
        )
        Project.objects.create(
            title="Spam Project",
            url="https://spam.example.com",
            short_description="Spam.",
            published=True,
            active=True,
            might_be_spam=True,
        )

        request = RequestFactory().get("/projects/")
        view = ProjectListView()
        view.setup(request)

        self.assertEqual(list(view.get_queryset()), [visible])

    def test_project_list_can_order_by_like_count(self):
        User = get_user_model()
        users = [
            User.objects.create_user(username=f"user-{index}", email=f"user-{index}@example.com") for index in range(3)
        ]
        less_liked = Project.objects.create(
            title="Less Liked",
            url="https://less-liked.example.com",
            short_description="Less liked.",
            published=True,
            active=True,
            updated_date=timezone.now() - timedelta(days=1),
        )
        more_liked = Project.objects.create(
            title="More Liked",
            url="https://more-liked.example.com",
            short_description="More liked.",
            published=True,
            active=True,
            updated_date=timezone.now() - timedelta(days=2),
        )
        Like.objects.create(author=users[0], project=less_liked, like=True)
        Like.objects.create(author=users[1], project=more_liked, like=True)
        Like.objects.create(author=users[2], project=more_liked, like=True)

        request = RequestFactory().get("/projects/", {"order_by": "like"})
        view = ProjectListView()
        view.setup(request)

        self.assertEqual(list(view.get_queryset())[:2], [more_liked, less_liked])

    def test_project_list_annotates_like_count_and_user_like_state(self):
        User = get_user_model()
        user = User.objects.create_user(username="liker", email="liker@example.com")
        other_user = User.objects.create_user(username="other-liker", email="other-liker@example.com")
        project = Project.objects.create(
            title="Annotated Project",
            url="https://annotated.example.com",
            short_description="Annotated.",
            published=True,
            active=True,
        )
        Like.objects.create(author=user, project=project, like=True)
        Like.objects.create(author=other_user, project=project, like=False)

        request = RequestFactory().get("/projects/")
        request.user = user
        view = ProjectListView()
        view.setup(request)

        annotated_project = view.get_queryset().get(id=project.id)
        self.assertEqual(annotated_project.like_count, 1)
        self.assertTrue(annotated_project.user_has_liked)


class LikeMigrationTests(TestCase):
    def test_dedupe_likes_keeps_preferred_like_per_author_project_pair(self):
        migration = importlib.import_module("projects.migrations.0031_like_unique_author_project")

        class FakeGroupQuery:
            def __init__(self, groups):
                self.groups = groups

            def annotate(self, **kwargs):
                return self

            def filter(self, **kwargs):
                return [group for group in self.groups if group["count"] > kwargs["count__gt"]]

        class FakeLikeQuery:
            def __init__(self, manager, likes):
                self.manager = manager
                self.likes = likes

            def order_by(self, *fields):
                likes = self.likes
                for field in reversed(fields):
                    reverse = field.startswith("-")
                    field_name = field.removeprefix("-")
                    likes = sorted(likes, key=lambda like: getattr(like, field_name), reverse=reverse)
                return likes

            def delete(self):
                ids_to_delete = {like.id for like in self.likes}
                self.manager.likes = [like for like in self.manager.likes if like.id not in ids_to_delete]

        class FakeLikeManager:
            def __init__(self, likes):
                self.likes = likes

            def values(self, *fields):
                groups = {}
                for like in self.likes:
                    key = tuple(getattr(like, field) for field in fields)
                    groups.setdefault(key, {field: getattr(like, field) for field in fields} | {"count": 0})
                    groups[key]["count"] += 1
                return FakeGroupQuery(groups.values())

            def filter(self, **kwargs):
                if "id__in" in kwargs:
                    ids = set(kwargs["id__in"])
                    return FakeLikeQuery(self, [like for like in self.likes if like.id in ids])

                return FakeLikeQuery(
                    self,
                    [
                        like
                        for like in self.likes
                        if like.author_id == kwargs["author_id"] and like.project_id == kwargs["project_id"]
                    ],
                )

        like_manager = FakeLikeManager(
            [
                SimpleNamespace(id=1, author_id=1, project_id=1, like=False, modified=3),
                SimpleNamespace(id=2, author_id=1, project_id=1, like=True, modified=1),
                SimpleNamespace(id=3, author_id=1, project_id=1, like=True, modified=2),
                SimpleNamespace(id=4, author_id=2, project_id=1, like=True, modified=1),
            ]
        )

        class FakeLike:
            objects = like_manager

        class FakeApps:
            def get_model(self, app_label, model_name):
                self.app_label = app_label
                self.model_name = model_name
                return FakeLike

        fake_apps = FakeApps()

        migration.dedupe_likes(fake_apps, schema_editor=None)

        self.assertEqual(fake_apps.app_label, "projects")
        self.assertEqual(fake_apps.model_name, "Like")
        self.assertEqual([like.id for like in like_manager.likes], [3, 4])
