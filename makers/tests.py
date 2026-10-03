import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from webpack_boilerplate import utils as webpack_utils

from projects.models import Project

from .models import Maker


class MakerPublicProjectTests(TestCase):
    def setUp(self):
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

        self.owner = get_user_model().objects.create_user(username="maker-owner")
        self.maker = Maker.objects.create(first_name="Public", last_name="Maker", slug="public-maker", user=self.owner)
        self.public = Project.objects.create(
            title="Visible Django project", url="https://visible.example.com", maker=self.maker, published=True
        )
        self.hidden = []
        for title, flags in [
            ("Unpublished project", {"published": False}),
            ("Inactive project", {"published": True, "active": False}),
            ("Spam project", {"published": True, "might_be_spam": True}),
        ]:
            self.hidden.append(
                Project.objects.create(
                    title=title, url=f"https://hidden.example.com/{len(self.hidden)}", maker=self.maker, **flags
                )
            )

    def assert_public_cards_only(self):
        response = self.client.get(self.maker.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["public_projects"]), [self.public])
        self.assertContains(response, self.public.get_absolute_url())
        self.assertEqual(self.client.get(self.public.get_absolute_url()).status_code, 200)
        for project in self.hidden:
            self.assertNotContains(response, project.get_absolute_url())
            self.assertNotContains(response, project.title)
        self.assertContains(response, '<link rel="canonical"')
        self.assertContains(response, '"@type": "Person"')

    def test_anonymous_profile_only_links_to_public_projects(self):
        self.assert_public_cards_only()
        for project in self.hidden:
            self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)

    def test_owner_profile_keeps_public_cards_without_changing_private_detail_access(self):
        self.client.force_login(self.owner)
        self.assert_public_cards_only()
        for project in self.hidden:
            self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 200)

    def test_profile_with_no_public_projects_has_no_empty_projects_section(self):
        self.public.active = False
        self.public.save(update_fields=["active"])
        response = self.client.get(self.maker.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<h3")
        self.assertNotContains(response, self.public.title)
        self.assertEqual(Project.objects.filter(maker=self.maker).count(), 4)
