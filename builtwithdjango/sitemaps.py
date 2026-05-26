from django.contrib import sitemaps
from django.contrib.sitemaps import GenericSitemap
from django.urls import reverse

from blog.models import Post
from developers.models import Developer
from jobs.models import Job
from makers.models import Maker
from podcast.models import Episode
from projects.models import Project


class StaticViewSitemap(sitemaps.Sitemap):
    """Generate Sitemap for the site"""

    priority = 0.5
    protocol = "https"

    def items(self):
        """Identify items that will be in the Sitemap

        Returns:
            List: urlNames that will be in the Sitemap
        """
        return [
            "home",
            "uses",
            "support",
            "advertize",
            "submit_project",
            "projects",
            "makers",
            "developers",
            "podcast_episodes",
            "blog",
            "articles",
            "jobs",
            "post_job",
            "newsletter_home",
            "generate_django_secret_page",
            "format_html_view",
        ]

    def location(self, item):
        """Get location for each item in the Sitemap

        Args:
            item (str): Item from the items function

        Returns:
            str: Url for the sitemap item
        """
        return reverse(item)


sitemaps = {
    "static": StaticViewSitemap,
    "blog": GenericSitemap(
        {"queryset": Post.objects.filter(status=Post.PUBLISHED), "date_field": "created"},
        priority=0.9,
        protocol="https",
    ),
    "projects": GenericSitemap(
        {
            "queryset": Project.objects.filter(published=True, active=True, might_be_spam=False),
            "date_field": "date_added",
        },
        priority=0.85,
        protocol="https",
    ),
    "jobs": GenericSitemap(
        {
            "queryset": Job.objects.filter(approved=True),
            "date_field": "created_datetime",
        },
        priority=0.8,
        protocol="https",
    ),
    "podcast": GenericSitemap(
        {"queryset": Episode.objects.all(), "date_field": "created_datetime"}, priority=0.8, protocol="https"
    ),
    "makers": GenericSitemap(
        {
            "queryset": Maker.objects.filter(projects__published=True).order_by("pk").distinct(),
            "date_field": "updated_date",
        },
        priority=0.7,
        protocol="https",
    ),
    "developers": GenericSitemap(
        {
            "queryset": Developer.objects.filter(looking_for_a_job=True),
            "date_field": "modified",
        },
        priority=0.7,
        protocol="https",
    ),
}
