from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from blog.models import Post
from builtwithdjango.sitemaps import StaticViewSitemap, sitemaps
from developers.models import Developer
from jobs.models import Job
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
        visible_project = Project.objects.create(
            title="Visible Project",
            url="https://visible.example.com",
            short_description="Visible in sitemap.",
            published=True,
            active=True,
            might_be_spam=False,
        )
        Project.objects.create(
            title="Spam Project",
            url="https://spam.example.com",
            short_description="Hidden from sitemap.",
            published=True,
            active=True,
            might_be_spam=True,
        )

        self.assertEqual(list(sitemaps["blog"].items()), [published_post])
        self.assertEqual(list(sitemaps["projects"].items()), [visible_project])


class SeoPageRenderTests(TestCase):
    def setUp(self):
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
            location="Madrid, Spain",
        )

        job_response = self.client.get(job.get_absolute_url())
        developer_response = self.client.get(developer.get_absolute_url())

        self.assertEqual(job_response.status_code, 200)
        self.assertEqual(developer_response.status_code, 200)
        self.assertIn('"@type": "JobPosting"', job_response.content.decode())
        self.assertIn('"@type": "Person"', developer_response.content.decode())
