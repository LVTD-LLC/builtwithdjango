import json
import tempfile
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import Resolver404, resolve, reverse
from django.utils import timezone
from webpack_boilerplate import utils as webpack_utils

from blog.content import Post
from blog.testing import make_post
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


class PublishedLinkRedirectTests(SimpleTestCase):
    def test_published_aliases_redirect_directly_and_preserve_queries(self):
        aliases = {
            "/guides": "/blog/",
            "/tutorials": "/blog/",
            "/showcase": "/projects/",
            "/tools/secret-key-generator": "/tools/django-secret/",
            "/tools/html-formatter": "/tools/format-html/",
        }
        query = "?utm_source=guide&tag=one&tag=two&next=https%3A%2F%2Fexample.com"
        for alias, destination in aliases.items():
            for suffix in ("", "/"):
                for method in (self.client.get, self.client.head):
                    with self.subTest(alias=alias, suffix=suffix, method=method.__name__):
                        self.assertRedirects(
                            method(alias + suffix + query),
                            destination + query,
                            status_code=301,
                            fetch_redirect_response=False,
                        )

    def test_aliases_do_not_mask_missing_resources(self):
        for path in ("/guides/social-auth/", "/guides/missing/", "/showcase/missing/", "/tools/missing/"):
            with self.subTest(path=path), self.assertRaises(Resolver404):
                resolve(path)


class SeoSitemapTests(TestCase):
    def test_sitemap_excludes_submission_form_without_changing_login_redirect(self):
        Site.objects.update_or_create(pk=1, defaults={"domain": "builtwithdjango.com", "name": "Built with Django"})
        Site.objects.clear_cache()
        response = self.client.get("/sitemap.xml")

        self.assertEqual(response.status_code, 200)
        locations = {
            node.text
            for node in ElementTree.fromstring(response.content).iter(
                "{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
            )
        }
        self.assertIn("https://builtwithdjango.com/projects/", locations)
        self.assertNotIn("https://builtwithdjango.com/projects/new/", locations)
        self.assertRedirects(
            self.client.get(reverse("submit_project")),
            f"{reverse('account_login')}?next={reverse('submit_project')}",
            fetch_redirect_response=False,
        )

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
        published_post = make_post(
            self,
            title="Published Guide",
            description="Visible in sitemap.",
            author=author,
            slug="published-guide",
            content="Content",
            status=Post.PUBLISHED,
        )
        make_post(
            self,
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

    def test_article_index_is_reachable_from_home_and_guides_without_exposing_drafts(self):
        article = make_post(self, slug="community-note", type="ARTICLE", author=self.author)
        guide = make_post(self, slug="practical-guide", type="TUTORIAL", author=self.author)
        draft = make_post(self, slug="draft-note", type="ARTICLE", status="DR", author=self.author)
        article_index = reverse("articles")

        for path in (reverse("home"), reverse("blog")):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                footer = html.split('<footer class="bw-footer">', 1)[1].split("</footer>", 1)[0]
                self.assertIn(f'href="{article_index}"', footer)
                if path == reverse("blog"):
                    main = html.split('<main id="main-content"', 1)[1].split("</main>", 1)[0]
                    self.assertIn(f'href="{article_index}"', main)
                    self.assertIn("Explore Django articles", main)
                    self.assertIn(f'href="{guide.get_absolute_url()}"', main)

        response = self.client.get(article_index)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn(f'href="{article.get_absolute_url()}"', html)
        self.assertNotIn(f'href="{draft.get_absolute_url()}"', html)
        self.assertNotIn(f'href="{guide.get_absolute_url()}"', html)
        self.assertIn(f'<link rel="canonical" href="http://localhost:8000{article_index}" />', html)
        self.assertNotIn('<meta name="robots"', html)
        self.assertEqual(html.count("<h1 "), 1)
        self.assertIn('"@type": "CollectionPage"', html)

    def test_blog_post_detail_renders_article_metadata(self):
        post = make_post(
            self,
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

    def test_project_pagination_has_bounded_numbered_links_and_preserves_filters(self):
        for index in range(28):
            Project.objects.create(
                title=f"Navigation Project {index}",
                url=f"https://navigation-{index}.example.com",
                published=True,
                active=True,
                might_be_spam=False,
                is_open_source=True,
            )

        with patch("projects.views.ProjectListView.paginate_by", 1):
            first = self.client.get("/projects/")
            html = first.content.decode()
            self.assertIn('aria-label="Go to project page 28"', html)
            self.assertIn('href="?page=28"', html)
            self.assertIn('aria-current="page" aria-label="Page 1"', html)
            self.assertNotIn('aria-label="Previous project page"', html)

            middle = self.client.get("/projects/?order_by=like&is_open_source=true&page=14")
            html = middle.content.decode()
            self.assertIn('href="?order_by=like&amp;is_open_source=true&amp;page=28"', html)
            self.assertIn('aria-current="page" aria-label="Page 14"', html)
            self.assertIn('<meta name="robots" content="noindex,follow" />', html)
            self.assertLessEqual(len(list(middle.context["pagination_range"])), 11)
            self.assertIn('aria-label="Go to project page 1"', html)

            last = self.client.get("/projects/?page=28")
            html = last.content.decode()
            self.assertNotIn('aria-label="Next project page"', html)
            self.assertIn('href="?page=1"', html)
            self.assertIn('<link rel="canonical" href="http://localhost:8000/projects/?page=28" />', html)

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
        tutorial = make_post(
            self,
            title="Tutorial Listing Overlap",
            description="A tutorial that should stay on the guides page.",
            author=self.author,
            slug="tutorial-listing-overlap",
            content="Tutorial content",
            status=Post.PUBLISHED,
            type=Post.TUTORIAL,
        )
        article = make_post(
            self,
            title="Article Listing Result",
            description="An article that belongs on the articles page.",
            author=self.author,
            slug="article-listing-result",
            content="Article content",
            status=Post.PUBLISHED,
            type=Post.ARTICLE,
        )
        update = make_post(
            self,
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
