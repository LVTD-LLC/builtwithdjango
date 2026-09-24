---
id: 12
created: '2024-08-07 11:21:38.655442+00:00'
modified: '2024-08-07 11:23:17.097453+00:00'
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

All the code in this tutorial will be in [this PR](https://github.com/builtwithdjango/basic-django/pull/6/files), so you can follow along.


## Help

If at any step of this tutorial something goes wrong you have the following options to get back on track:

- read the allauth docs: [https://docs.allauth.org/](https://docs.allauth.org/)
- comment down below this post
- tweet me @builtwitdjango
- send me an email: rasul@builtwithdjango.com

You can also check out other tutorials on Social Auth to get a different prospective or to cross check in case something goes wrong. I strongly recommend [Will Vincent's tutorial](https://learndjango.com/tutorials/django-allauth-tutorial).

## Preparation

-  Install django-allauth `poetry add "django-allauth[socialaccount]"` ([primer on using poetry if you need it](https://builtwithdjango.com/blog/basic-django-setup))
-  Add the following 2 lines to the `installed_apps` variable in `settings.py:

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
   
   Note 3: I got the `Authorization callback URL` value from the [django-allauth page on Github Authentication](https://docs.allauth.org/en/latest/socialaccount/providers/github.html). In general if you are adding Social Authentication via django-allauth, make sure to use the relevant provider page, as it will have all the necessary information.
   
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
        "VERIFIED_EMAIL": True,
        "APP": {
            "client_id": env("GITHUB_CLIENT_ID"),
            "secret": env("GITHUB_CLIENT_SECRET"),
        },
    },
}
```

Note 1: VERIFIED_EMAIL key tells our app that anyone who authed through github will count as a Verified email we can trust.

Note 2: In the app key we are loading the env vars we just saved in our .env file.

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
- `pnpm run start` in another

Head over to `http://127.0.0.1:8000/` in your browser. This is what I'm seeing:

![basic-django home page with github link](https://res.cloudinary.com/built-with-django/image/upload/v1723025632/blog-images/CleanShot_2024-08-06_at_12.30.05_2x_jla0ps.png)

- Click the new link... This will lead you to `http://127.0.0.1:8000/users/github/login/` that looks like this:

![basic-django continu with github login raw screen](https://res.cloudinary.com/built-with-django/image/upload/v1723025690/blog-images/CleanShot_2024-08-06_at_12.32.08_2x_ami0df.png)

Don't worry, we will style this page later.

- Click continue. You should be directed to the Github login page:
  ![github auth screen](https://res.cloudinary.com/built-with-django/image/upload/v1723025761/blog-images/CleanShot_2024-08-06_at_12.50.14_2x_jp8dqu.png)

- Once you go through, you should be redirected to your home page and see something like this:
  ![basic-django authed github home page](https://res.cloudinary.com/built-with-django/image/upload/v1723025802/blog-images/CleanShot_2024-08-06_at_12.53.56_2x_vrf0gw.png)

If everything worked fine, then congrats! If not, comment down below, I'll do my best to help you!

In the next tutorial will will style those new pages and make a few quality of life adjustments.