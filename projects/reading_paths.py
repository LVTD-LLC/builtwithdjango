"""Curated links to existing, source-pinned exercises in the project directory."""

from datetime import date

READING_PATHS_MODIFIED = date(2026, 11, 17)

READING_PATHS = {
    "pinry": {
        "repository": "https://github.com/pinry/pinry",
        "anchor": "read-pinry-permissions",
        "description": "Trace Pinry's private-board filtering through its API view, serializer, and tests.",
    },
    "baby-buddy": {
        "repository": "https://github.com/babybuddy/babybuddy",
        "anchor": "read-baby-buddy-notes",
        "description": "Follow Baby Buddy's note pages from URL routes to class-based views and tests.",
    },
}


def reading_path_for(project):
    path = READING_PATHS.get(project.slug)
    if (
        path
        and project.published
        and project.active
        and not project.might_be_spam
        and project.github_url.rstrip("/").lower() == path["repository"]
    ):
        return path
    return None
