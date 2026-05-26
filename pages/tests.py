from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from blog.models import Post
from jobs.models import Job
from pages.views import HomeView
from projects.models import Project


class HomeViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_home_jobs_only_include_recent_approved_jobs(self):
        recent_job = Job.objects.create(
            title="Recent Django role",
            listing_url="https://example.com/jobs/recent",
            company_name="Recent Co",
            approved=True,
            created_datetime=timezone.now() - timedelta(days=2),
        )
        old_job = Job.objects.create(
            title="Old Django role",
            listing_url="https://example.com/jobs/old",
            company_name="Old Co",
            approved=True,
            created_datetime=timezone.now() - timedelta(days=61),
        )
        unapproved_job = Job.objects.create(
            title="Unapproved Django role",
            listing_url="https://example.com/jobs/unapproved",
            company_name="Draft Co",
            approved=False,
            created_datetime=timezone.now(),
        )

        request = self.factory.get("/")
        view = HomeView()
        view.setup(request)

        with patch("pages.views.static", return_value="/static/vendors/images/logo.png"):
            context = view.get_context_data()

        jobs = list(context["jobs"])
        self.assertIn(recent_job, jobs)
        self.assertNotIn(old_job, jobs)
        self.assertNotIn(unapproved_job, jobs)

    def test_home_projects_and_guides_show_six_items(self):
        author = get_user_model().objects.create_user(
            username="guide-author",
            email="guide-author@example.com",
            password="test-pass",
        )
        for index in range(7):
            Project.objects.create(
                title=f"Project {index}",
                url=f"https://example.com/projects/{index}",
                short_description="A Django project worth studying.",
                published=True,
                active=True,
            )
            Post.objects.create(
                title=f"Guide {index}",
                description="A practical Django guide.",
                author=author,
                slug=f"guide-{index}",
                content="Guide content",
                type=Post.TUTORIAL,
                status=Post.PUBLISHED,
            )

        request = self.factory.get("/")
        view = HomeView()
        view.setup(request)

        with patch("pages.views.static", return_value="/static/vendors/images/logo.png"):
            context = view.get_context_data()

        self.assertEqual(len(context["projects"]), 6)
        self.assertEqual(len(context["guides"]), 6)
