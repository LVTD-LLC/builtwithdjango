from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.crypto import salted_hmac
from django.views.generic import FormView, TemplateView
from django_q.tasks import async_task

from builtwithdjango.analytics import capture
from jobs.models import Job
from podcast.models import Episode
from projects.models import Project

from .forms import NewsletterSignupForm, getWeeklyTemplateForm
from .models import Emails


class NewsletterSignupView(FormView):
    template_name = "newsletter/email-form.html"
    form_class = NewsletterSignupForm
    success_url = reverse_lazy("newsletter_thanks")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not settings.NEWSLETTER_LISTMONK_URL or not settings.NEWSLETTER_LIST_UUID:
            return self.unavailable(form)
        # Only trust the nearest proxy's appended address when explicitly enabled.
        ip = request.META.get("REMOTE_ADDR", "unknown")
        if settings.NEWSLETTER_TRUST_PROXY:
            ip = request.META.get("HTTP_X_FORWARDED_FOR", ip).split(",")[-1].strip()
        key = "newsletter:rate:" + salted_hmac("newsletter-ip", ip).hexdigest()
        try:
            if cache.add(key, 1, timeout=3600):
                count = 1
            else:
                count = cache.incr(key)
        except Exception:
            # Do not send mail if the shared abuse-control store is unavailable.
            return self.unavailable(form)
        if count > 10:
            form.add_error(None, "Too many requests. Please try again in an hour.")
            response = self.render_to_response(self.get_context_data(form=form), status=429)
            response["Retry-After"] = "3600"
            return response
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form), status=400)
        if form.cleaned_data["company"]:
            return HttpResponseRedirect(self.get_success_url())
        return self.form_valid(form)

    def unavailable(self, form):
        form.is_valid()
        form.add_error(None, "Newsletter signup is temporarily unavailable. Please try again shortly.")
        return self.render_to_response(self.get_context_data(form=form), status=503)

    def form_valid(self, form):
        try:
            response = requests.post(
                settings.NEWSLETTER_LISTMONK_URL.rstrip("/") + "/api/public/subscription",
                json={"email": form.cleaned_data["user_email"], "list_uuids": [settings.NEWSLETTER_LIST_UUID]},
                timeout=(3, 10),
                allow_redirects=False,
            )
            payload = response.json() if response.status_code == 200 else None
            data = payload.get("data") if isinstance(payload, dict) else None
            if not isinstance(data, dict) or data.get("has_optin") is not True:
                raise ValueError("Unexpected newsletter response")
        except (requests.RequestException, ValueError):
            # Never log submitted addresses, provider response bodies or exceptions.
            return self.unavailable(form)
        source = self.request.POST.get("source", "site")
        if source not in {"newsletter component", "newsletter page", "makers", "modal"}:
            source = "site"
        capture(self.request, "newsletter confirmation requested", properties={"subscription_source": source})
        return HttpResponseRedirect(self.get_success_url())


class NewsletterThanksView(TemplateView):
    template_name = "newsletter/sucessfull-email-submit.html"


@user_passes_test(lambda user: user.is_staff)
def getWeeklyTemplateView(request):
    form = getWeeklyTemplateForm(request.POST)
    if form.is_valid():
        days = form.cleaned_data["days"]
        filter_date = datetime.today() - timedelta(days=days)
        projects = Project.objects.filter(
            created_date__gte=filter_date,
            published=True,
            might_be_spam=False,
            active=True,
        )
        jobs = Job.objects.filter(created_datetime__gte=filter_date).filter(approved=True)
        podcast_episodes = Episode.objects.filter(created_datetime__gte=filter_date)
        context = {
            "projects": projects,
            "jobs": jobs,
            "podcasts": podcast_episodes,
        }
        send_mail(
            "Weekly Email Template",
            render_to_string("newsletter/weekly-newsletter-template.md", context),
            "Built with Django <rasul@builtwithdjango.com>",
            ["Built with Django <rasul@builtwithdjango.com>"],
        )
        capture(
            request,
            "weekly newsletter preview requested",
            properties={
                "days": days,
                "project_count": projects.count(),
                "job_count": jobs.count(),
                "podcast_episode_count": podcast_episodes.count(),
            },
        )
        return redirect("home")
    return render(request, "newsletter/send-weekly-email.html", {"form": form})
