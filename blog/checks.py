from django.core.checks import Error, register
from django.core.exceptions import ImproperlyConfigured

from .content import all_posts


@register()
def check_blog_content(app_configs, **kwargs):
    try:
        posts = all_posts()
        if not posts:
            raise ImproperlyConfigured("No repository blog posts found")
    except ImproperlyConfigured as exc:
        return [Error(str(exc), id="blog.E001")]
    return []
