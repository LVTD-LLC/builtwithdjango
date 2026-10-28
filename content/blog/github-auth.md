---
id: 12
created: '2024-08-07 11:21:38.655442+00:00'
modified: '2026-10-28 08:45:00+00:00'
title: Adding Github Auth to Django
slug: github-auth
status: PB
description: Adding our first Social Authentication (Github) via django-allauth
unsplashID: wX2L8L-fGeA
icon: image/upload/v1723029699/blog-post-icon-prod/mtyxvu5iddzix44tkn4l.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 7
  name: Github
  slug: github
- id: 10
  name: Authentication
  slug: authentication
- id: 15
  name: django-allauth
  slug: django-allauth
author: 1
---
## Introduction

In the [previous post we have setup Environment Variable](https://builtwithdjango.com/blog/env-vars) in our [basic-django](https://github.com/builtwithdjango/basic-django) app.

In this tutorial we will be adding our first Social Authentication (Github) via [django-allauth](https://allauth.org/).

If you haven't setup django-allauth in your app, make sure to go through the [previous tutorial on it](https://builtwithdjango.com/blog/user-authentication). We are setting it up from scratch there.

The [original example PR](https://github.com/builtwithdjango/basic-django/pull/6/files) is historical context. The configuration and local checks below were verified with Python 3.11, Django 5.2.18 and django-allauth 65.19.7. They extend the account setup above; this is not a test of your production OAuth app or email delivery.


## Help

If at any step of this tutorial something goes wrong you have the following options to get back on track:

- read the allauth docs: [https://docs.allauth.org/](https://docs.allauth.org/)
- comment down below this post
- tweet me @builtwitdjango
- send me an email: rasul@builtwithdjango.com

You can also check out other tutorials on Social Auth to get a different prospective or to cross check in case something goes wrong. I strongly recommend [Will Vincent's tutorial](https://learndjango.com/tutorials/django-allauth-tutorial).

## Preparation

-  Install django-allauth `poetry add "django-allauth[socialaccount]==65.19.7"` ([primer on using poetry if you need it](https://builtwithdjango.com/blog/basic-django-setup))
-  Add the following 2 lines to the existing `INSTALLED_APPS` list in `settings.py`:

```
INSTALLED_APPS = [
	...
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
	...
]
``` 

- Make sure that the allauth url is in the `urls.py` file:

```
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")), # this
    path("", include("pages.urls")),
]
```
  
- Create our app on Github by going to the following link: [https://github.com/settings/applications/new](https://github.com/settings/applications/new).
  
  Fill out the form. Here is what I did:
   ![github new app form](https://res.cloudinary.com/built-with-django/image/upload/v1723025075/blog-images/CleanShot_2024-08-03_at_12.09.12_2x_vwdnug.png)
   
   Note 1: I have added `local` to the end of the application name. This is useful, since when we create a production version we will setup a separate app.
   
   Note 2: Make sure Enable Device Flow is not checked. This is for CLI apps without browser.
   
   Note 3: With `path("accounts/", include("allauth.urls"))` above, set the local homepage URL to `http://127.0.0.1:8000/` and the **Authorization callback URL** to:

   ```text
   http://127.0.0.1:8000/accounts/github/login/callback/
   ```

   Keep the scheme, host, port and path consistent with the address you actually open. `localhost` and `127.0.0.1` are different hosts. A different URL prefix changes the callback too. The [allauth GitHub provider reference](https://docs.allauth.org/en/latest/socialaccount/providers/github.html) documents this local callback. Use a separate OAuth app with your real HTTPS domain for production; do not copy the development address there.
   
   > If you are having any trouble with specific authentication type, let me know I will create a separate tutorial for that.
   
- Click 'Register Application'.

- Copy the `Client ID` value and added to your .env file like so:
```
GITHUB_CLIENT_ID="Ov23lisVB..." # this will be unique for you  
```

- Click on the `Generate a new client secret` and also add it to your `.env` file like so:
```
GITHUB_CLIENT_SECRET="e5f7ecd..." # this will be unique for you
```

Note: If you need a primer on environment variables, check them out [here](https://builtwithdjango.com/blog/env-vars).

## Let's get to business

Now we have everything in place to continue.

- Run `poetry run python manage.py migrate` to add all the tables required by `django-allauth`.

- Add the following to the bottom of your `settings.py` file:
```
SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": env("GITHUB_CLIENT_ID"),
            "secret": env("GITHUB_CLIENT_SECRET"),
        },
    },
}
```

Do not add a blanket `VERIFIED_EMAIL` override. In the tested version, the GitHub provider reads each email address's `verified` flag from GitHub. Setting that override to `True` also upgrades provider-unverified addresses to verified inside allauth; signing in with GitHub is not proof that every returned address is verified. See the [GitHub provider implementation](https://github.com/pennersr/django-allauth/blob/65.19.7/allauth/socialaccount/providers/github/provider.py) and [provider configuration](https://docs.allauth.org/en/latest/socialaccount/provider_configuration.html).

Keep your account email-verification policy from the [authentication tutorial](/blog/user-authentication). Requiring an email field is not the same as verifying ownership. Do not enable automatic matching or connecting to existing local accounts solely to make a test login succeed.

The `APP` dictionary loads the environment variables from the previous step. Keep `.env` untracked and never share the client secret in code, logs or screenshots. If a secret was exposed, revoke it and replace it; deleting a file does not revoke it.

This example configures the OAuth app **in settings only**. Do not also create a GitHub `SocialApp` with the same client ID in Django admin: conflicting app definitions can cause `MultipleObjectsReturned`. If you use the admin instead, omit the settings `APP` block and associate that record with the correct Site. The [provider configuration guide](https://docs.allauth.org/en/latest/socialaccount/provider_configuration.html) explains both approaches.

Leave additional scopes unset for this sign-in example. With the required email signup field from the preceding tutorial, the tested provider requests `user:email`; it does not need access to your repositories. Request broader permissions only for a feature that actually needs them.

- Run `poetry run python manage.py runserver` to make sure everything run smoothly. If it does let's continue.

Another powerful feature of django-allauth is that they provide you with all the goodies. You are about to see.

Just add the following line to your `home.html` file:
```html
{% extends "base.html" %}
{% load socialaccount %}  <!-- new -->

{% block content %}

  ...
	
  {% if user.is_authenticated %}
    <p>Username: {{ user.username }}</p>
    <p>Email: {{ user.email }}</p>
    <a href="{% url 'account_logout' %}">Logout</a>
  {% else %}
    <a class="p-2 text-blue-500 rounded-md border" href="{% url 'account_login' %}">Login</a>
    <a class="p-2 text-blue-500 rounded-md border" href="{% url 'account_signup' %}">Signup</a>
    <a class="p-2 text-blue-500 rounded-md border" href="{% provider_login_url 'github' %}">Sign Up with GitHub</a> <!-- new -->
  {% endif %}

{% endblock content %}
```

Note 1: I added some Tailwind style classes to make it easier to see the result. The main point is the new 'github' link.

Note 2: If you are wondering where all of these other links are, I've talked about this in [another allauth tutorial](https://builtwithdjango.com/blog/user-authentication) (without social auth).

After adding these lines to our html file, let's run our server:

- `poetry run python manage.py runserver` in one terminal tab
- If your project has a separate frontend watcher, run its existing command too. No frontend build tool is required for the authentication handshake itself.

Head over to `http://127.0.0.1:8000/` in your browser. This is what I'm seeing:

![basic-django home page with github link](https://res.cloudinary.com/built-with-django/image/upload/v1723025632/blog-images/CleanShot_2024-08-06_at_12.30.05_2x_jla0ps.png)

- Click the new link... This will lead you to `http://127.0.0.1:8000/accounts/github/login/` that looks like this:

![basic-django continu with github login raw screen](https://res.cloudinary.com/built-with-django/image/upload/v1723025690/blog-images/CleanShot_2024-08-06_at_12.32.08_2x_ami0df.png)

The older screenshot may show a different prefix. With this tutorial's URL configuration, use `/accounts/`, not `/users/`.

Keep this confirmation step. A GET request displays the page; its CSRF-protected POST starts the GitHub handshake. Do not enable `SOCIALACCOUNT_LOGIN_ON_GET` to skip it: allauth [recommends requiring POST](https://docs.allauth.org/en/latest/socialaccount/configuration.html#socialaccount-login-on-get). If you replace the link with a custom direct-login form, include Django's CSRF token.

- Click continue. You should be directed to the Github login page:
  ![github auth screen](https://res.cloudinary.com/built-with-django/image/upload/v1723025761/blog-images/CleanShot_2024-08-06_at_12.50.14_2x_jp8dqu.png)

- Once you go through, you should be redirected to your home page and see something like this:
  ![basic-django authed github home page](https://res.cloudinary.com/built-with-django/image/upload/v1723025802/blog-images/CleanShot_2024-08-06_at_12.53.56_2x_vrf0gw.png)

## Check the local flow

Before testing a real account, run:

```bash
poetry run python manage.py check
poetry run python manage.py shell -c "from django.urls import reverse; print(reverse('github_login')); print(reverse('github_callback'))"
```

With the URL include above, the output paths should be `/accounts/github/login/` and `/accounts/github/login/callback/`.

Then walk through the flow in your browser:

1. While signed out, open the GitHub link. Expect a confirmation page, not an immediate external redirect.
2. Continue using that page's form. The GitHub authorization URL should contain your client ID, a `state` parameter and the callback URL you registered. Do not post the full URL or tokens publicly.
3. Authorize your local OAuth app on GitHub. A new user may need to finish the allauth signup form; returning users can log in. Additional email verification depends on your configured policy and the provider's email data.
4. Confirm you reach your named `home` route, then use the logout confirmation screen. Test again while signed out.

The isolated checks for this update verified URL resolution, the GET confirmation, rejection of a POST without CSRF, the authorization redirect, rejection of mismatched callback state, and preservation of provider-verified versus unverified email flags. They used fictional credentials and email data, not a real GitHub token exchange. Complete the browser authorization with your own local OAuth app before considering your integration tested.

## If the flow stops

- **404 before GitHub:** compare the path with the `reverse()` output. A `/users/` link does not match an `accounts/` include.
- **Callback mismatch:** compare the exact address registered on GitHub with the `redirect_uri` in the authorization request. Keep one local host throughout the flow; retain the trailing slash.
- **Missing or multiple apps:** choose settings-based `APP` configuration or the admin-based `SocialApp`, and check the current Site when using the admin.
- **State or CSRF failure:** restart from the login page in the same browser session. Check cookie and HTTPS/proxy settings for your deployment; do not disable state validation or CSRF protection.
- **Unexpected signup or email screen:** check the account signup and verification settings before changing trust rules. The console backend in the preceding tutorial does not deliver mail.

If everything works, you now have a locally tested GitHub sign-in path. Before deployment, configure your production HTTPS callback, secret storage and real mail backend separately.

In the next tutorial will will style those new pages and make a few quality of life adjustments.