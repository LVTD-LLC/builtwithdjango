from django.views.generic import DetailView, ListView

from builtwithdjango.analytics import capture
from newsletter.forms import NewsletterSignupForm

from .models import Post


class PostListView(ListView):
    model = Post
    template_name = "blog/all_posts.html"
    queryset = Post.objects.filter(type=Post.TUTORIAL, status=Post.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class ArticleListView(ListView):
    model = Post
    template_name = "blog/all_articles.html"
    queryset = Post.objects.filter(status="PB").order_by("-created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"

    def get_queryset(self):
        return Post.objects.filter(status=Post.PUBLISHED)

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
