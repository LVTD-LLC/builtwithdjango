import json
from urllib.parse import urlencode, urljoin

from django import template
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

register = template.Library()
_json_ld_escapes = {
    ord(">"): "\\u003E",
    ord("<"): "\\u003C",
    ord("&"): "\\u0026",
}


def _site_url():
    return getattr(settings, "SITE_URL", "").rstrip("/")


@register.simple_tag(takes_context=True)
def absolute_url(context, value="/"):
    if not value:
        value = "/"

    value = str(value).strip()
    if value.startswith(("http://", "https://")):
        return value
    if value.startswith("//"):
        return f"https:{value}"

    site_url = _site_url()
    if site_url:
        return urljoin(f"{site_url}/", value.lstrip("/"))

    request = context.get("request")
    if request:
        return request.build_absolute_uri(value)

    return value


@register.simple_tag(takes_context=True)
def canonical_url(context, path=None):
    request = context.get("request")
    if path is None and request:
        path = request.path
    return absolute_url(context, path or "/")


@register.filter
def json_ld(value):
    value = json.dumps(value, cls=DjangoJSONEncoder, ensure_ascii=False).translate(_json_ld_escapes)
    return mark_safe(value)


@register.filter
def seo_text(value, length=300):
    try:
        length = int(length)
    except (TypeError, ValueError):
        length = 300
    text = strip_tags(str(value or "")).replace("\n", " ").strip()
    return " ".join(text.split())[:length]


@register.simple_tag
def osig_image(title, subtitle="", eyebrow="", site="x", image_url="", style="base", font="markerfelt"):
    params = {
        "style": style,
        "site": site,
        "font": font,
        "title": title,
    }
    if subtitle:
        params["subtitle"] = subtitle
    if eyebrow:
        params["eyebrow"] = eyebrow
    if image_url:
        params["image_url"] = image_url
    return f"https://osig.app/g?{urlencode(params)}"
