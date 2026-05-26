import importlib
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

import requests
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from .models import Like, Project
from .tasks import save_screenshot
from .utils import create_tweet
from .views import ProjectListView


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

    def test_analyze_content_uses_pydantic_ai_v1_output_api(self):
        class FakeAgent:
            kwargs = None
            prompt = None

            def __init__(self, *args, **kwargs):
                self.output_type = kwargs["output_type"]
                FakeAgent.kwargs = kwargs

            def run_sync(self, prompt):
                FakeAgent.prompt = prompt
                return SimpleNamespace(
                    output=self.output_type(
                        target_audience="Django teams",
                        content_summary="A concise summary",
                        might_be_spam=False,
                        key_features="- Feature",
                        pain_points="- Pain point",
                        usage_instructions="Use it from the browser",
                        page_links="- Home - https://ai.example.com",
                        content_language="English",
                    )
                )

        project = Project.objects.create(
            title="AI Analyze Project",
            url="https://ai.example.com",
            short_description="A Django AI project",
            page_title="AI Project",
            page_description="Useful project",
            page_content_markdown="Project content",
            page_content_html="<p>Project content</p>",
            published=True,
        )

        with patch("projects.models.Agent", FakeAgent):
            self.assertTrue(project.analyze_content())

        project.refresh_from_db()
        self.assertNotIn("result_type", FakeAgent.kwargs)
        self.assertEqual(FakeAgent.kwargs["output_type"].__name__, "ContentAnalysis")
        self.assertIn("AI Project", FakeAgent.prompt)
        self.assertEqual(project.target_audience, "Django teams")
        self.assertEqual(project.content_summary, "A concise summary")
        self.assertEqual(project.content_language, "English")
        self.assertTrue(project.published)

    def test_create_tweet_uses_pydantic_ai_v1_output_api(self):
        class FakeAgent:
            kwargs = None
            deps = None

            def __init__(self, *args, **kwargs):
                self.output_type = kwargs["output_type"]
                FakeAgent.kwargs = kwargs

            def instructions(self, func):
                return func

            async def run(self, prompt, *, deps):
                FakeAgent.deps = deps
                return SimpleNamespace(output=self.output_type(tweet_text="A useful launch tweet"))

        project = Project.objects.create(
            title="Tweet Project",
            url="https://tweet.example.com",
            short_description="A project worth tweeting about",
            twitter_url="https://x.com/example",
            target_audience="Django developers",
            content_summary="Tweetable summary",
            key_features="- Fast",
            pain_points="- Boilerplate",
        )

        with patch("projects.utils.Agent", FakeAgent):
            tweet_text = async_to_sync(create_tweet)(project.id)

        self.assertNotIn("result_type", FakeAgent.kwargs)
        self.assertEqual(FakeAgent.kwargs["output_type"].__name__, "TweetContent")
        self.assertEqual(FakeAgent.kwargs["deps_type"].__name__, "ProjectContext")
        self.assertEqual(FakeAgent.deps.title, "Tweet Project")
        self.assertEqual(tweet_text, "A useful launch tweet")


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

    def test_fetch_page_content_saves_jina_reader_response(self):
        project = Project.objects.create(
            title="Readable Project",
            url="https://readable.example.com",
            short_description="A project.",
        )
        html_response = Mock(text="<html>Project</html>")
        html_response.raise_for_status.return_value = None
        jina_response = Mock()
        jina_response.raise_for_status.return_value = None
        jina_response.json.return_value = {
            "data": {
                "title": "Readable",
                "description": "A readable project.",
                "content": "# Readable",
            }
        }

        with patch("projects.models.requests.get", side_effect=[html_response, jina_response]):
            self.assertTrue(project.fetch_page_content())

        project.refresh_from_db()
        self.assertEqual(project.page_title, "Readable")
        self.assertEqual(project.page_description, "A readable project.")
        self.assertEqual(project.page_content_markdown, "# Readable")
        self.assertEqual(project.page_content_html, "<html>Project</html>")
        self.assertIsNotNone(project.date_scraped)


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


class ProjectTaskTests(TestCase):
    def test_save_screenshot_publishes_project_when_screenshot_succeeds(self):
        project = Project.objects.create(
            title="Screenshot Project",
            url="https://screenshot.example.com",
            short_description="A project.",
        )
        response = Mock(content=b"image-bytes")
        response.raise_for_status.return_value = None

        with patch("projects.tasks.requests.get", return_value=response) as get:
            self.assertTrue(save_screenshot(project.title))

        project.refresh_from_db()
        self.assertTrue(project.published)
        self.assertTrue(project.homepage_screenshot.name.endswith(".png"))
        self.assertEqual(get.call_args.kwargs["timeout"], 30)

    def test_save_screenshot_returns_false_when_screenshot_fetch_fails(self):
        project = Project.objects.create(
            title="Broken Screenshot Project",
            url="https://broken-screenshot.example.com",
            short_description="A project.",
        )
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("failed")

        with patch("projects.tasks.requests.get", return_value=response):
            self.assertFalse(save_screenshot(project.title))

        project.refresh_from_db()
        self.assertFalse(project.published)
