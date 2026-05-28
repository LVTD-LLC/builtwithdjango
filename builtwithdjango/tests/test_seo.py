import json
import tempfile
from datetime import timedelta
from pathlib import Path

from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from webpack_boilerplate import utils as webpack_utils

from blog.models import Post
from builtwithdjango.sitemaps import StaticViewSitemap, sitemaps
from developers.models import Developer
from jobs.models import Job
from makers.models import Maker
from podcast.models import Episode
from projects.models import Project


class SeoTemplateTagTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(SITE_URL="https://builtwithdjango.com")
    def test_absolute_url_uses_site_url_for_relative_paths(self):
        template = Template("{% absolute_url '/media/share.png' %}")
        html = template.render(Context({"request": self.factory.get("/ignored/")}))

        self.assertEqual(html, "https://builtwithdjango.com/media/share.png")

    @override_settings(SITE_URL="https://builtwithdjango.com")
    def test_seo_meta_outputs_canonical_and_absolute_share_image(self):
        request = self.factory.get("/ignored/?utm_source=test")
        html = render_to_string(
            "components/seo_meta.html",
            {
                "title": "Django Projects | Built with Django",
                "description": "Discover projects built with Django.",
                "canonical_path": "/projects/",
                "image": "/media/share.png",
            },
            request=request,
        )

        self.assertIn('<link rel="canonical" href="https://builtwithdjango.com/projects/" />', html)
        self.assertIn('<meta property="og:image" content="https://builtwithdjango.com/media/share.png" />', html)
        self.assertIn('<meta name="twitter:image" content="https://builtwithdjango.com/media/share.png" />', html)

    def test_json_ld_filter_outputs_valid_json_string(self):
        template = Template('"name": {{ value|json_ld }}')
        html = template.render(Context({"value": 'Django "Guide"\nTest'}))

        self.assertEqual(html, '"name": "Django \\"Guide\\"\\nTest"')

    def test_json_ld_filter_escapes_script_breakout_characters(self):
        template = Template("{{ value|json_ld }}")
        html = template.render(Context({"value": "</script><script>alert(1)</script>&"}))

        self.assertNotIn("</script>", html)
        self.assertIn("\\u003C/script\\u003E", html)
        self.assertIn("\\u0026", html)

    @override_settings(SITE_URL="https://builtwithdjango.com")
    def test_robots_txt_declares_crawl_rules_and_sitemap(self):
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        robots_txt = response.content.decode()
        self.assertIn("User-agent: *", robots_txt)
        self.assertIn("Allow: /", robots_txt)
        self.assertIn("Disallow: /users/", robots_txt)
        self.assertIn("Sitemap: https://builtwithdjango.com/sitemap.xml", robots_txt)


class SeoSitemapTests(TestCase):
    def test_static_sitemap_includes_public_index_pages(self):
        items = StaticViewSitemap().items()

        self.assertIn("projects", items)
        self.assertIn("makers", items)
        self.assertIn("developers", items)
        self.assertIn("articles", items)
        self.assertIn("newsletter_home", items)

    def test_content_sitemaps_only_include_indexable_records(self):
        author = get_user_model().objects.create_user(
            username="seo-author",
            email="seo-author@example.com",
            password="test-pass",
        )
        published_post = Post.objects.create(
            title="Published Guide",
            description="Visible in sitemap.",
            author=author,
            slug="published-guide",
            content="Content",
            status=Post.PUBLISHED,
        )
        Post.objects.create(
            title="Draft Guide",
            description="Hidden from sitemap.",
            author=author,
            slug="draft-guide",
            content="Content",
            status=Post.DRAFT,
        )
        visible_maker = Maker.objects.create(first_name="Visible", last_name="Maker", slug="visible-maker")
        spam_maker = Maker.objects.create(first_name="Spam", last_name="Maker", slug="spam-maker")
        inactive_maker = Maker.objects.create(first_name="Inactive", last_name="Maker", slug="inactive-maker")

        visible_project = Project.objects.create(
            title="Visible Project",
            url="https://visible.example.com",
            short_description="Visible in sitemap.",
            published=True,
            active=True,
            might_be_spam=False,
            maker=visible_maker,
        )
        Project.objects.create(
            title="Spam Project",
            url="https://spam.example.com",
            short_description="Hidden from sitemap.",
            published=True,
            active=True,
            might_be_spam=True,
            maker=spam_maker,
        )
        Project.objects.create(
            title="Inactive Project",
            url="https://inactive.example.com",
            short_description="Hidden from sitemap.",
            published=True,
            active=False,
            might_be_spam=False,
            maker=inactive_maker,
        )
        current_job = Job.objects.create(
            title="Current Django Engineer",
            listing_url="https://jobs.example.com/current-django-engineer",
            company_name="Current Co",
            approved=True,
            created_datetime=timezone.now() - timedelta(days=1),
        )
        Job.objects.create(
            title="Expired Django Engineer",
            listing_url="https://jobs.example.com/expired-django-engineer",
            company_name="Expired Co",
            approved=True,
            created_datetime=timezone.now() - timedelta(days=61),
        )
        Job.objects.create(
            title="Unapproved Django Engineer",
            listing_url="https://jobs.example.com/unapproved-django-engineer",
            company_name="Unapproved Co",
            approved=False,
        )

        self.assertEqual(list(sitemaps["blog"].items()), [published_post])
        self.assertEqual(list(sitemaps["projects"].items()), [visible_project])
        self.assertEqual(list(sitemaps["jobs"]().items()), [current_job])
        self.assertEqual(list(sitemaps["makers"].items()), [visible_maker])


class SeoPageRenderTests(TestCase):
    def setUp(self):
        self.webpack_manifest_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.webpack_manifest_dir.cleanup)

        manifest_path = Path(self.webpack_manifest_dir.name) / "manifest.json"
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
        self.webpack_settings = self.settings(
            WEBPACK_LOADER={
                "CACHE": False,
                "MANIFEST_FILE": str(manifest_path),
            },
        )
        self.webpack_settings.enable()
        self.addCleanup(self.webpack_settings.disable)
        self.addCleanup(webpack_utils._loaders.clear)

        self.author = get_user_model().objects.create_user(
            username="page-author",
            email="page-author@example.com",
            password="test-pass",
        )

    def test_blog_post_detail_renders_article_metadata(self):
        post = Post.objects.create(
            title='Django "SEO" Guide',
            description="A practical guide to Django SEO.",
            author=self.author,
            slug="django-seo-guide",
            content="Guide content",
            status=Post.PUBLISHED,
        )

        response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('<meta property="og:type" content="article" />', html)
        self.assertIn('<link rel="canonical" href="http://localhost:8000/blog/django-seo-guide" />', html)
        self.assertIn('"headline": "Django \\"SEO\\" Guide"', html)

    def test_project_detail_renders_twitter_image_not_duplicate_og_image(self):
        project = Project.objects.create(
            title="SEO Project",
            url="https://project.example.com",
            short_description="A project with clean metadata.",
            published=True,
            active=True,
        )

        response = self.client.get(project.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertEqual(html.count('property="og:image"'), 1)
        self.assertIn('name="twitter:image"', html)
        self.assertIn('<link rel="canonical" href="http://localhost:8000/projects/seo-project" />', html)

    def test_project_detail_excludes_non_public_projects(self):
        project = Project.objects.create(
            title="Hidden SEO Project",
            url="https://hidden-project.example.com",
            short_description="This project should not be publicly indexable.",
            published=False,
            active=True,
            might_be_spam=False,
        )

        response = self.client.get(project.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_project_page_two_self_canonicalizes(self):
        for index in range(13):
            Project.objects.create(
                title=f"Paginated Project {index}",
                url=f"https://paginated-project-{index}.example.com",
                short_description="A project used to exercise pagination metadata.",
                published=True,
                active=True,
                might_be_spam=False,
            )

        response = self.client.get("/projects/?page=2")

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('<link rel="canonical" href="http://localhost:8000/projects/?page=2" />', html)
        self.assertNotIn('<meta name="robots"', html)

    def test_project_filters_are_noindexed(self):
        response = self.client.get("/projects/?order_by=like")

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('<link rel="canonical" href="http://localhost:8000/projects/" />', html)
        self.assertIn('<meta name="robots" content="noindex,follow" />', html)

    def test_job_and_developer_detail_render_structured_data(self):
        job = Job.objects.create(
            title="Django Engineer",
            listing_url="https://jobs.example.com/django-engineer",
            company_name="Example Co",
            approved=True,
        )
        developer = Developer.objects.create(
            user=self.author,
            looking_for_a_job=True,
            title="Senior Django Developer",
            description="Builds production Django apps.",
            capacity="FTC",
            location="",
        )

        job_response = self.client.get(job.get_absolute_url())
        developer_response = self.client.get(developer.get_absolute_url())

        self.assertEqual(job_response.status_code, 200)
        self.assertEqual(developer_response.status_code, 200)
        job_html = job_response.content.decode()
        self.assertIn('<meta property="og:type" content="website" />', job_html)
        self.assertIn('"@type": "JobPosting"', job_html)
        self.assertIn('"validThrough":', job_html)
        self.assertNotIn('"address": ""', job_html)
        developer_html = developer_response.content.decode()
        self.assertIn('"@type": "Person"', developer_html)
        self.assertNotIn('"@type": "PostalAddress"', developer_html)
        self.assertNotIn('"addressLocality": ""', developer_html)

    def test_job_detail_excludes_unapproved_jobs(self):
        job = Job.objects.create(
            title="Unapproved Django Engineer",
            listing_url="https://jobs.example.com/unapproved-django-engineer",
            company_name="Example Co",
            approved=False,
        )

        response = self.client.get(job.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_all_jobs_archive_is_noindexed(self):
        Job.objects.create(
            title="Archived Django Engineer",
            listing_url="https://jobs.example.com/archived-django-engineer",
            company_name="Example Co",
            approved=True,
            created_datetime=timezone.now() - timedelta(days=61),
        )

        response = self.client.get("/jobs/all")

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('<link rel="canonical" href="http://localhost:8000/jobs/all" />', html)
        self.assertIn('<meta name="robots" content="noindex,follow" />', html)

    def test_all_jobs_archive_paginates_and_self_canonicalizes_pages(self):
        for index in range(31):
            Job.objects.create(
                title=f"Archived Django Engineer {index}",
                listing_url=f"https://jobs.example.com/archived-django-engineer-{index}",
                company_name="Example Co",
                approved=True,
                created_datetime=timezone.now() - timedelta(days=61),
            )

        response = self.client.get("/jobs/all?page=2")

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('<link rel="canonical" href="http://localhost:8000/jobs/all?page=2" />', html)
        self.assertIn("Page 2 of 2", html)
        self.assertIn('<meta name="robots" content="noindex,follow" />', html)

    def test_expired_job_detail_is_noindexed_but_keeps_expiration_schema(self):
        job = Job.objects.create(
            title="Expired Django Engineer",
            listing_url="https://jobs.example.com/expired-django-engineer",
            company_name="Example Co",
            approved=True,
            created_datetime=timezone.now() - timedelta(days=61),
        )

        response = self.client.get(job.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('<meta name="robots" content="noindex,follow" />', html)
        self.assertIn('"validThrough":', html)

    def test_article_listing_excludes_tutorials(self):
        tutorial = Post.objects.create(
            title="Tutorial Listing Overlap",
            description="A tutorial that should stay on the guides page.",
            author=self.author,
            slug="tutorial-listing-overlap",
            content="Tutorial content",
            status=Post.PUBLISHED,
            type=Post.TUTORIAL,
        )
        article = Post.objects.create(
            title="Article Listing Result",
            description="An article that belongs on the articles page.",
            author=self.author,
            slug="article-listing-result",
            content="Article content",
            status=Post.PUBLISHED,
            type=Post.ARTICLE,
        )
        update = Post.objects.create(
            title="Update Listing Result",
            description="A non-article update that should stay out of the articles page.",
            author=self.author,
            slug="update-listing-result",
            content="Update content",
            status=Post.PUBLISHED,
            type=Post.UPDATE,
        )

        response = self.client.get("/blog/articles/")

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn(article.title, html)
        self.assertNotIn(update.title, html)
        self.assertNotIn(tutorial.title, html)

    def test_podcast_detail_uses_default_website_og_type(self):
        episode = Episode.objects.create(
            title="Podcast SEO",
            slug="podcast-seo",
            thumbnail="podcast/episode.png",
            details="A podcast episode about Django SEO.",
        )

        response = self.client.get(episode.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('<meta property="og:type" content="website" />', html)
        self.assertIn('"@type": "PodcastEpisode"', html)
