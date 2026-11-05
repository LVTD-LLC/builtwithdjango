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

    def __init__(self, *args, **kwargs):
        super(PostJob, self).__init__(*args, **kwargs)

        for fieldname in [
            "title",
            "listing_url",
            "email",
            "min_yearly_salary",
            "max_yearly_salary",
            "company_name",
        ]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {
                    "class": "shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                }
            )

    class Meta:
        model = Job
        fields = [
            "title",
            "listing_url",
            "email",
            "min_yearly_salary",
            "max_yearly_salary",
            "company_name",
        ]
