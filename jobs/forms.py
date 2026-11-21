from django import forms
from django.forms import ModelForm

from .abuse import verify_job_challenge
from .models import Job


class PostJob(ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("Unable to accept this submission.")
        if not self.errors and not verify_job_challenge(self.data.get("cf-turnstile-response", "")):
            raise forms.ValidationError("Please complete the verification and submit your job again.")
        return cleaned

    class Meta:
        model = Job
        fields = ["listing_url"]
