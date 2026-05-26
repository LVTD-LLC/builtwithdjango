from django.views.generic import DetailView, ListView

from builtwithdjango.analytics import capture
from newsletter.views import NewsletterSignupForm

from .models import Episode


class EpisodeListView(ListView):
    model = Episode
    template_name = "podcast/all_episodes.html"
    queryset = Episode.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context


class EpisodeDetailView(DetailView):
    model = Episode
    template_name = "podcast/episode_detail.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        capture(
            request,
            "podcast episode viewed",
            properties={
                "episode_id": self.object.id,
                "episode_title": self.object.title,
                "episode_slug": self.object.slug,
                "episode_number": getattr(self.object, "number", None),
            },
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newsletter_form"] = NewsletterSignupForm

        return context
