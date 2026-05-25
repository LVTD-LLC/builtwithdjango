from django.template.loader import render_to_string
from django.test import TestCase

from .models import Job


class JobItemTemplateTests(TestCase):
    def test_job_item_omits_empty_submitted_datetime(self):
        job = Job.objects.create(
            title="Django developer",
            listing_url="https://example.com/jobs/django-developer",
            company_name="Example Co",
            approved=True,
        )

        html = render_to_string("components/job-item.html", {"job": job})

        self.assertIn("Django developer", html)
        self.assertNotIn("la-clock", html)
        self.assertNotIn(" ago", html)
