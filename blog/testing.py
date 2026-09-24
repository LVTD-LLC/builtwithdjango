"""File-backed fixtures for blog consumers; never create legacy database posts."""

import tempfile
from pathlib import Path

import yaml
from django.test import override_settings
from django.utils import timezone

from .content import read_post


def make_post(test, **kwargs):
    if not hasattr(test, "blog_directory"):
        directory = tempfile.TemporaryDirectory()
        test.addCleanup(directory.cleanup)
        test.blog_directory = Path(directory.name)
        override = override_settings(BLOG_CONTENT_DIR=test.blog_directory)
        override.enable()
        test.addCleanup(override.disable)
    data = {
        "id": len(list(test.blog_directory.glob("*.md"))) + 1,
        "author": 1,
        "title": "Test guide",
        "description": "A guide.",
        "slug": "test-guide",
        "content": "# Test guide\n\nMarkdown **body**.",
        "status": "PB",
        "type": "TUTORIAL",
        "level": "BEGINNER",
        "created": timezone.now().isoformat(),
        "modified": timezone.now().isoformat(),
        "tag_list": [],
        "unsplashID": "",
        "icon": "",
    }
    data.update(kwargs)
    if hasattr(data["author"], "pk"):
        data["author"] = data["author"].pk
    content = data.pop("content")
    path = test.blog_directory / (data["slug"] + ".md")
    path.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + content, encoding="utf-8")
    return read_post(path)
