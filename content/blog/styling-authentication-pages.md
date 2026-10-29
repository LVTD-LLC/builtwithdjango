---
id: 7
created: '2022-10-03 16:27:45.268000+00:00'
modified: '2026-10-29 08:45:00+00:00'
title: Styling django-allauth Authentication Pages
slug: styling-authentication-pages
status: PB
description: In this tutorial we will learn to overwrite the default template styling of the django-allauth authentication
  forms.
unsplashID: G3GL5lJygz8
icon: image/upload/v1664814489/blog-post-icon-prod/afkmdtjcrkasd7415wnd.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 11
  name: Frontend
  slug: frontend
- id: 13
  name: TailwindCSS
  slug: tailwindcss
- id: 14
  name: Templates
  slug: templates
- id: 15
  name: django-allauth
  slug: django-allauth
author: 1
---
## Style the form, keep the authentication flow

Django-allauth supplies the signup view, validation and account flow. You can change how its form looks without rebuilding that behavior or assembling error HTML in Python.

This walkthrough overrides one signup template, renders the configured fields and styles their errors with ordinary CSS. It was checked with Python 3.11, Django 5.2.18 and django-allauth 65.19.7, using username, email and two password fields. It is a local password-signup example, not a complete theme for social login, passkeys or MFA.

Start with the [working account setup](/blog/user-authentication). The older [basic-django example PR](https://github.com/builtwithdjango/basic-django/pull/1/files) records the original 2022 design; it is not the current dependency baseline. If your CSS is already built with Tailwind, keep that pipeline: the markup below does not require another CSS package.

## Make sure Django finds your template

Keep your existing template settings and add the project template directory to `DIRS`. With the usual `BASE_DIR` setting, the relevant entries inside `TEMPLATES` are:

```python
"DIRS": [BASE_DIR / "templates"],
"APP_DIRS": True,
```

The project directory is searched before app templates with Django's default loader setup. A custom loader configuration needs the equivalent ordering. These entries belong inside your existing DjangoTemplates backend, not in a second `TEMPLATES` assignment that drops context processors.

Create `templates/base.html` if you do not already have a site layout:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block head_title %}My Django site{% endblock %}</title>
  </head>
  <body>
    <main>{% block content %}{% endblock %}</main>
  </body>
</html>
```

An existing layout is fine too; use its real block names. Extending `base.html` does not create a `content` block in a layout that calls it something else.

## Override account/signup.html

Create `templates/account/signup.html`. The path is relative to the template directory; do not create `templates/allauth/account/signup.html`.

```html
{% extends "base.html" %}
{% block head_title %}Create your account{% endblock %}
{% block content %}
  <section class="signup-card" aria-labelledby="signup-heading">
    <h1 id="signup-heading">Create your account</h1>
    <p>Already registered? <a href="{% url 'account_login' %}">Sign in</a>.</p>
    <form method="post" action="{% url 'account_signup' %}">
      {% csrf_token %}
      {% if form.non_field_errors %}
        <div class="signup-errors" role="alert">
          {% for error in form.non_field_errors %}<p>{{ error }}</p>{% endfor %}
        </div>
      {% endif %}
      {% for hidden in form.hidden_fields %}
        {{ hidden }}
        {% for error in hidden.errors %}<p class="signup-errors">{{ error }}</p>{% endfor %}
      {% endfor %}
      {% for field in form.visible_fields %}
        <div class="signup-field">
          {{ field.label_tag }}
          {{ field }}
          {% if field.help_text %}
            <div id="{{ field.auto_id }}_helptext" class="signup-help">{{ field.help_text }}</div>
          {% endif %}
          {% if field.errors %}
            <ul id="{{ field.auto_id }}_error" class="signup-errors">
              {% for error in field.errors %}<li>{{ error }}</li>{% endfor %}
            </ul>
          {% endif %}
        </div>
      {% endfor %}
      {% if redirect_field_value %}
        <input type="hidden" name="{{ redirect_field_name }}" value="{{ redirect_field_value }}">
      {% endif %}
      <button type="submit">Create account</button>
    </form>
  </section>
{% endblock %}
```

The field loop follows the configured signup form rather than assuming every project requires the same four fields. It preserves widget names, generated IDs, password autocomplete attributes and bound values. `label_tag` connects each visible label to its input. Django 5.2 also associates ordinary field errors and help text using these `_error` and `_helptext` IDs. Keep those IDs if you change the wrappers.

The form action uses the named URL. If the prerequisite includes allauth under `accounts/`, signup is `/accounts/signup/`, not `/users/signup/`. To check your own prefix, run:

```bash
poetry run python manage.py shell -c "from django.urls import reverse; print(reverse('account_signup'))"
```

Keep the CSRF token and POST method. The redirect field preserves allauth's continuation value; it does not replace the view's redirect-safety checks. Do not add a hidden `remember` input to signup: session persistence belongs to the login flow.

## Style inputs and errors together

Add this to the stylesheet your layout already loads. To try the self-contained example, put it inside a `<style>` element in the example base template's `<head>`; projects with a restrictive Content Security Policy should use their allowed external stylesheet.

```css
.signup-card { max-width: 28rem; margin: 2rem auto; padding: 1.25rem; color: #17251d; }
.signup-field { margin: 1rem 0; }
.signup-field label { display: block; margin-bottom: .35rem; font-weight: 600; }
.signup-field input:not([type="checkbox"]):not([type="radio"]) {
  box-sizing: border-box; width: 100%; padding: .7rem;
  border: 1px solid #66746c; border-radius: .35rem;
}
.signup-card a { color: #166534; text-decoration: underline; }
.signup-card button {
  padding: .75rem 1rem; border: 0; border-radius: .35rem;
  background: #166534; color: white; font-weight: 600; cursor: pointer;
}
.signup-card :is(input, button, a):focus-visible { outline: 3px solid #2563eb; outline-offset: 3px; }
.signup-help { margin-top: .35rem; color: #46564c; font-size: .9rem; }
.signup-errors { margin: .5rem 0; padding: .75rem 1.5rem; border: 1px solid #b91c1c; color: #991b1b; background: #fef2f2; }
.signup-field input[aria-invalid="true"] { border-color: #b91c1c; }
```

No `django-widget-tweaks`, custom `SignupForm` or `ACCOUNT_FORMS` entry is needed for this version. Existing application-specific validation can stay in Python; visual error markup stays in the template.

### Keep error messages escaped

Use `{{ error }}` in the loops, without a `safe` filter. Do not join error strings into HTML in an f-string and then mark the result safe. A custom validator might include user-supplied text: rendering that text as HTML can introduce an injection vulnerability. The former `DivErrorList` recipe did exactly this for a fixture error containing HTML; that is why this example no longer uses it. This is not a claim that the standard allauth validators or a deployed site were exploited.

Django's ordinary template autoescaping handles plain error strings. Do not deliberately mark untrusted validator output safe upstream. See the [Django forms API](https://docs.djangoproject.com/en/5.2/ref/forms/api/) for validation and error handling.

## Check the local flow

Start Django with `poetry run python manage.py runserver`. If your existing stylesheet needs a frontend watcher, start that separately using your project's command.

1. Open the URL returned by `reverse('account_signup')`. Confirm the new heading and visible, correctly associated labels.
2. Submit empty required fields, different passwords and a weak password. Browser validation may stop an empty form before it reaches Django; submit a malformed POST with Django's test client to check server-side errors too. Confirm errors stay beside their fields and non-field errors remain visible.
3. Submit an existing username and, with unique email enabled, an existing email. Confirm the bound form displays errors without losing the entered non-password values.
4. Test a custom validation message containing `<strong>example</strong>`. It should appear as literal text, not bold markup. Check hidden-field errors too if your form adds hidden fields.
5. Submit valid disposable local credentials. Confirm the expected redirect and account creation. With email verification enabled, also test the appropriate verification flow using a local mail backend; the example's local checks do not prove production email delivery.
6. Check at a narrow viewport and navigate by keyboard. Labels, validation messages and the submit button should remain readable, with visible focus.

The template changes presentation, not your signup policy. Recheck fields, redirects and verification after changing allauth settings or upgrading the package.

## When to use allauth's layout and element overrides

Overriding `account/signup.html` is useful for a deliberately custom page, but it replaces that page's upstream markup. This example intentionally omits social-provider buttons and other optional signup modes. For GitHub sign-in, follow the [provider setup guide](/blog/github-auth) and preserve the provider controls required by your flow.

For a consistent theme across login, signup and account-management screens, consider allauth's `allauth/layouts/entrance.html` and `allauth/elements/` overrides instead. They can retain more of the package's built-in flow. Check the [current allauth template documentation](https://docs.allauth.org/en/latest/common/templates.html) and the templates shipped with your installed version: the modern element/slot structure is not the same as the historical template this tutorial originally copied.

Next, apply the same approach to one other account page, testing its actual behavior before sharing a common theme.
