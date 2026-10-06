from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from blog.content import Post
from blog.testing import make_post
from jobs.models import Job
from pages.views import HomeView
from projects.models import Like, Project


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
            make_post(
                self,
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

    def test_home_projects_include_like_metadata(self):
        user = get_user_model().objects.create_user(username="home-liker", email="home-liker@example.com")
        other_user = get_user_model().objects.create_user(username="other-home-liker", email="other@example.com")
        project = Project.objects.create(
            title="Liked Home Project",
            url="https://example.com/home-liked",
            short_description="A liked home project.",
            published=True,
            active=True,
        )
        Like.objects.create(author=user, project=project, like=True)
        Like.objects.create(author=other_user, project=project, like=False)

        request = self.factory.get("/")
        request.user = user
        view = HomeView()
        view.setup(request)

        with patch("pages.views.static", return_value="/static/vendors/images/logo.png"):
            context = view.get_context_data()

        home_project = context["projects"][0]
        self.assertEqual(home_project.like_count, 1)
        self.assertTrue(home_project.user_has_liked)


class RedesignDiscoveryTests(TestCase):
    def test_home_excludes_spam_and_keeps_secondary_destinations_in_footer(self):
        Project.objects.create(
            title="Hidden spam",
            slug="hidden-spam",
            url="https://spam.example",
            published=True,
            active=True,
            might_be_spam=True,
        )
        response = self.client.get("/")
        html = response.content.decode()
        header = html.split("<header", 1)[1].split("</header>", 1)[0]
        footer = html.split("<footer", 1)[1].split("</footer>", 1)[0]
        self.assertNotContains(response, "Hidden spam")
        for path in ("/tools/django-secret/", "/tools/format-html/", "/podcast/", "/jobs/"):
            self.assertNotIn('href="' + path + '"', header)
            self.assertIn('href="' + path + '"', footer)
        self.assertNotContains(response, "Django teams are hiring")

    def test_project_search_is_server_rendered_and_preserves_visibility(self):
        for title, spam in [("Django Maps", False), ("Django Maps Spam", True), ("Other product", False)]:
            Project.objects.create(
                title=title,
                url="https://" + title.lower().replace(" ", "-") + ".example.com",
                published=True,
                active=True,
                might_be_spam=spam,
            )
        response = self.client.get("/projects/", {"q": "Maps"})
        titles = [p.title for p in response.context["page_obj"]]
        self.assertEqual(titles, ["Django Maps"])
        self.assertContains(response, "noindex,follow")

    def test_blog_search_and_type_filters_keep_drafts_private(self):
        for title, kind, status in [
            ("Learn Django", Post.TUTORIAL, Post.PUBLISHED),
            ("Django news", Post.ARTICLE, Post.PUBLISHED),
            ("Secret Django", Post.TUTORIAL, Post.DRAFT),
        ]:
            make_post(self, title=title, slug=title.lower().replace(" ", "-"), type=kind, status=status, content="Body")
        response = self.client.get("/blog/", {"q": "Django", "type": Post.TUTORIAL})
        self.assertEqual([p.title for p in response.context["object_list"]], ["Learn Django"])
        self.assertContains(response, "noindex,follow")

    def test_account_recovery_uses_shared_shell(self):
        response = self.client.get("/users/password/reset/")
        self.assertContains(response, "Primary navigation")
        self.assertContains(response, "bw-auth-content")
        self.assertContains(response, "noindex,nofollow")

    def test_search_with_no_results_has_reset_path(self):
        for path in ("/projects/", "/blog/"):
            response = self.client.get(path, {"q": "nonexistent-redesign-test-9876"})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Reset")
            self.assertContains(response, "noindex,follow")
