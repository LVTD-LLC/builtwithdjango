from django.urls import path
from django.views.generic import RedirectView

from .feeds import BlogFeed
from .views import PostDetailView, PostListView

urlpatterns = [
    path("", PostListView.as_view(), name="blog"),
    path("articles/", RedirectView.as_view(pattern_name="blog", permanent=True, query_string=True), name="articles"),
    path("<slug:slug>", PostDetailView.as_view(), name="post"),
    path("feed/rss", BlogFeed(), name="blog_feed"),
]
