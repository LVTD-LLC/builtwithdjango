from django.urls import path

from .feeds import ArticleFeed, BlogFeed
from .views import ArticleListView, CommentCreateView, PostDetailView, PostListView

urlpatterns = [
    path("", PostListView.as_view(), name="blog"),
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("<slug:slug>", PostDetailView.as_view(), name="post"),
    path(
        "<slug:slug>/create-comment",
        CommentCreateView.as_view(),
        name="create_guide_comment",
    ),
    path("feed/rss", BlogFeed(), name="blog_feed"),
    path("articles/feed/rss", ArticleFeed(), name="articles_feed"),
]
