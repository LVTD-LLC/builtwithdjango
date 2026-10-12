from django import forms
from django.forms import Form


class NewsletterSignupForm(Form):
    user_email = forms.EmailField(label="Email address", max_length=254)
    company = forms.CharField(required=False, widget=forms.HiddenInput)


class getWeeklyTemplateForm(Form):
    days = forms.IntegerField()
