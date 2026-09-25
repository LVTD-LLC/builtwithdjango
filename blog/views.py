from django.http import Http404
from django.views.generic import DetailView, ListView

from builtwithdjango.analytics import capture
from newsletter.forms import NewsletterSignupForm

from .content import Post, published_posts


class PostListView(ListView):
    template_name = "blog/all_posts.html"

    def get_queryset(self):
        return published_posts(Post.TUTORIAL)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class ArticleListView(ListView):
    template_name = "blog/all_articles.html"

    def get_queryset(self):
        return published_posts(Post.ARTICLE)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class PostDetailView(DetailView):
    template_name = "blog/post_detail.html"

    def get_object(self, queryset=None):
        for post in published_posts():
            if post.slug == self.kwargs["slug"]:
                return post
        raise Http404("Post not found")

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        capture(
            request,
            "post viewed",
            properties={
                "post_id": self.object.id,
                "post_title": self.object.title,
                "post_slug": self.object.slug,
                "post_type": self.object.type,
                "post_status": self.object.status,
            },
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context
