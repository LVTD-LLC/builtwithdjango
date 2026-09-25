"""Repository-backed posts. Legacy ORM models are a rollback archive only."""

import re
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import yaml
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware


@dataclass(frozen=True)
class Post:
    id: int
    author: int
    title: str
    description: str
    slug: str
    content: str
    status: str
    type: str
    level: str
    created: datetime
    modified: datetime
    tag_list: list
    unsplashID: str = ""
    icon: str = ""

    DRAFT = "DR"
    PUBLISHED = "PB"
    TUTORIAL = "TUTORIAL"
    ARTICLE = "ARTICLE"
    UPDATE = "UPDATE"
    INTERVIEW = "INTERVIEW"
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

    def get_absolute_url(self):
        return reverse("post", kwargs={"slug": self.slug})

    def get_type_display(self):
        return self.type

    def get_level_display(self):
        return self.level


def content_directory():
    return Path(getattr(settings, "BLOG_CONTENT_DIR", Path(settings.BASE_DIR) / "content" / "blog"))


def read_post(path):
    try:
        stat = path.stat()
    except OSError as exc:
        raise ImproperlyConfigured(f"Cannot read blog post {path.name}: {exc}") from exc
    return _read_post(path, stat.st_mtime_ns, stat.st_size)


@lru_cache(maxsize=512)
def _read_post(path, modified_ns, size):
    # Key by file version so development edits reload without parsing every file on every request.
    try:
        text = path.read_bytes().decode("utf-8")
        front_matter = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
        if front_matter is None:
            raise ValueError("expected YAML front matter")
        header, body = front_matter.group(1), text[front_matter.end() :]
        data = yaml.safe_load(header)
        if not isinstance(data, dict):
            raise ValueError("front matter must be a mapping")
        for key in ("created", "modified"):
            value = data.get(key)
            data[key] = value if isinstance(value, datetime) else parse_datetime(str(value))
            if data[key] is None or not is_aware(data[key]):
                raise ValueError(f"{key} must be a timezone-aware ISO timestamp")
        post = Post(content=body, **data)
        if not isinstance(post.slug, str) or not re.fullmatch(r"[-a-zA-Z0-9_]+", post.slug):
            raise ValueError("invalid slug")
        if path.stem != post.slug:
            raise ValueError("filename must match slug")
        if type(post.id) is not int or post.id < 1 or type(post.author) is not int or post.author < 1:
            raise ValueError("id and author must be positive integers")
        for field in ("title", "description", "unsplashID", "icon"):
            if not isinstance(getattr(post, field), str):
                raise ValueError(f"{field} must be a string")
        if not post.title.strip() or not post.content.strip():
            raise ValueError("title and content must not be empty")
        if post.status not in {Post.DRAFT, Post.PUBLISHED}:
            raise ValueError("invalid publication status")
        if post.type not in {Post.TUTORIAL, Post.ARTICLE, Post.UPDATE, Post.INTERVIEW}:
            raise ValueError("invalid post type")
        if post.level not in {"", Post.BEGINNER, Post.INTERMEDIATE, Post.ADVANCED}:
            raise ValueError("invalid difficulty level")
        if not isinstance(post.tag_list, list) or any(
            not isinstance(tag, dict)
            or set(tag) != {"id", "name", "slug"}
            or type(tag["id"]) is not int
            or not isinstance(tag["name"], str)
            or not (tag["slug"] is None or isinstance(tag["slug"], str))
            for tag in post.tag_list
        ):
            raise ValueError("invalid tag_list")
        return post
    except (ValueError, TypeError, OSError, yaml.YAMLError) as exc:
        raise ImproperlyConfigured(f"Invalid blog post {path.name}: {exc}") from exc


def all_posts():
    directory = content_directory()
    if not directory.is_dir():
        raise ImproperlyConfigured(f"Blog content directory does not exist: {directory}")
    posts = [read_post(path) for path in sorted(directory.glob("*.md"))]
    if len({post.slug for post in posts}) != len(posts) or len({post.id for post in posts}) != len(posts):
        raise ImproperlyConfigured("Blog post ids and slugs must be unique")
    return sorted(posts, key=lambda post: (post.created, post.id), reverse=True)


def published_posts(post_type=None):
    return [
        post for post in all_posts() if post.status == Post.PUBLISHED and (post_type is None or post.type == post_type)
    ]
