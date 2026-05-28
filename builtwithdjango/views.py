from django.conf import settings
from django.http import HttpResponse


def robots_txt(request):
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    if not site_url:
        site_url = request.build_absolute_uri("/").rstrip("/")

    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin-panel/",
        "Disallow: /api/",
        "Disallow: /stripe/",
        "Disallow: /users/",
        "",
        f"Sitemap: {site_url}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
