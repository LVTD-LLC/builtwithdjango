from types import SimpleNamespace
from unittest.mock import patch

from asgiref.sync import async_to_sync
from django.test import TestCase

from .models import Project
from .utils import create_tweet


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

            def system_prompt(self, func):
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
