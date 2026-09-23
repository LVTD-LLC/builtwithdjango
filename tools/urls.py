from django.urls import path, re_path
from django.views.generic import RedirectView

from .views import FormatHTMLView, GenerateDjangoSecret, format_html_endpoint, generate_django_secret

urlpatterns = [
    re_path(
        r"^secret-key-generator/?$",
        RedirectView.as_view(pattern_name="generate_django_secret_page", permanent=True, query_string=True),
    ),
    re_path(
        r"^html-formatter/?$",
        RedirectView.as_view(pattern_name="format_html_view", permanent=True, query_string=True),
    ),
    path("django-secret/", GenerateDjangoSecret.as_view(), name="generate_django_secret_page"),
    path("generate-secret/", generate_django_secret, name="generate_django_secret"),
    path("api/format-html/", format_html_endpoint, name="format_html_endpoint"),
    path("format-html/", FormatHTMLView.as_view(), name="format_html_view"),
]
