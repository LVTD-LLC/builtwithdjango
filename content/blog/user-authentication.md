---
id: 5
created: '2022-06-18 15:55:37.856000+00:00'
modified: '2026-10-07 07:00:00+00:00'
title: User Authentication in Django
slug: user-authentication
status: PB
description: In today's post, we will take care of Authentication. We will be setting up a Custom User model with
  the use of django-allauth.
unsplashID: Lexcm-6FHRU
icon: image/upload/v1659728533/blog-post-icon-prod/zat8kiaip1orhnw1mwcr.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 3
  name: Custom User Model
  slug: custom-user-model
- id: 10
  name: Authentication
  slug: authentication
author: 1
---
Update (08/06/2024): Added Middleware update in `settings.py`

In the [previous post](https://builtwithdjango.com/blog/django-version-control) we went through the process of setting up Version Control for our `basic-django` app.

In today's post, we will take care of [Authentication](https://en.wikipedia.org/wiki/Authentication).

[Django has authentication](https://docs.djangoproject.com/en/4.0/topics/auth/) built into it. For most cases what Django has to offer is fine, but if you ever want to customize or add to the Auth experience they [recommend customizing it](https://docs.djangoproject.com/en/4.0/topics/auth/customizing/). So, that's what we are going to do.

Together we will go through the process of creating a Custom User Model, integrating `django-allauth` to make out lives easier and to have an option to add social logins in the future, and finally add login, signup, logout logic to our `basic-django` app.

> Note: I'm a strong believer in looking at many sources when it comes to learning. I think it improves understanding of new material. If you agree with me on this, here are some other fantastic Django Authentication posts I encountered, when I was learning:
> 
> -   [Django Best Practices: Custom User Model](https://learndjango.com/tutorials/django-custom-user-model) by [Will Vincent](https://wsvincent.com)
> -   [Creating a Custom User Model in Django](https://testdriven.io/blog/django-custom-user-model/) by [Michael Herman](https://mherman.org)
> -   [How to Create a Custom Django User Model](https://www.codingforentrepreneurs.com/blog/how-to-create-a-custom-django-user-model/) by [Justin Mitchel](https://www.codingforentrepreneurs.com)

## Users App

Open up your Code Editor (for me it is VS Code) and open your Django project. Confirm everything is working (for example, by running `runserver`), and let's go.

Let's create a new "app" called users where we will have all the code relating to authentication.

```bash
poetry run python manage.py startapp users
```

> Note: If you haven't read the [previous post](https://builtwithdjango.com/blog/basic-django-setup), you might be wondering what is all this "poetry run…" stuff. Well, I like to use [Poetry](https://python-poetry.org) for dependency management. If you want to learn more, see [this post](https://builtwithdjango.com/blog/basic-django-setup).

You should see a new folder was created in your project called `users`. Awesome.

Now you want to head over to `settings.py` and add `users.apps.UsersConfig` to the `INSTALLED_APP` list. And while we are at it, add the following to the bottom of the `settings.py` file:

```python
# Authentication
AUTH_USER_MODEL = "users.CustomUser"
```

This will tell our Django app that we are using a Custom User Model. You might be wondering what is this CustomUser. You would be right, we haven't created it yet and that's what we are going to do now.

Head over to the `models.py` file under the `users` folder and add the following code:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    twitter_handle = models.CharField(max_length=20, blank=True)
```

`AbstractUser` already includes `first_name` and `last_name`. This example overrides their maximum length to 20 characters and adds `twitter_handle`; it does not introduce three new fields. If you do not need shorter names, omit those two overrides and keep Django's defaults. See the [Django 5.2 user fields reference](https://docs.djangoproject.com/en/5.2/ref/contrib/auth/#user-model).

Set `AUTH_USER_MODEL` before the first migration, and create `CustomUser` in the users app's initial migration. If you have already migrated a project with Django's default user, do not simply change this setting: follow the [custom-user migration guide](/blog/custom-user-model-migration-mid-project-django). Django explains the distinction in its [custom user model documentation](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#substituting-a-custom-user-model).

Once you are done setting this up, you can add more stuff, like Date of Birth, Profile Picture, other social links, or anything that your heart desires.

As you can see we named this model `CustomUser`, which is what we are referring to in the last line of `settings.py`.

Next, let's add some code that will help us see the new table in our Django Admin panel. Head over to the `admin.py` file under the `users` folder and add the following code.

Add the following to `users/admin.py`:

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = ["date_joined", "username", "email", "first_name", "last_name"]
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        (
            "Extra Fields",
            {
                "fields": (
                    "twitter_handle",
                )
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
```

Alright, now we are done with building the `Users` app. Now let's build the logic for the user signup and login.

## django-allauth

Run `poetry add django-allauth`.

The settings below use Django 5.2 and django-allauth 65.19.7. Check the [allauth quickstart](https://docs.allauth.org/en/latest/installation/quickstart.html) when using a different release. 

We are not going to do a social authentication, only email, and username, so no need to add `'allauth.socialaccount.providers.{app}',` to `INSTALLED_APPS`. 

Here is what the `INSTALLED_APPS` will look like after new lines:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",  # make sure this is present 
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages", # make sure this is present
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",  # new
    "allauth.account",   # new
    "users.apps.UsersConfig",
    # Keep your other project apps here.
]
```

Don't forget to add the new MIDDLEWARE line like here:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # new
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

Then, add the following to the bottom of `settings.py`:

```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
SITE_ID = 1

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGIN_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_REDIRECT_URL = "home"

ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_LOGIN_METHODS = {"username"}
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = True
```

`AUTHENTICATION_BACKENDS` is required to tell our application to use `django-allauth` for authentication.

The console email backend prints messages locally; it does not deliver email. Configure a real sending backend before deployment. Choose email verification deliberately:

```python
ACCOUNT_EMAIL_VERIFICATION = "optional"
# Use "mandatory" to require verification before login, or "none" to disable it.
```

The required `email*` signup field asks for an address; it does not prove ownership. The `*` suffix marks required fields. See [allauth account configuration](https://docs.allauth.org/en/latest/account/configuration.html) for signup, login and verification settings.

Keep `django.template.context_processors.request` in `TEMPLATES[0]["OPTIONS"]["context_processors"]`, as in Django's generated settings. Along with `AccountMiddleware`, this is part of the [allauth installation requirements](https://docs.allauth.org/en/latest/installation/quickstart.html).

`LOGIN_REDIRECT_URL` and `ACCOUNT_LOGOUT_REDIRECT_URL` point to the named `home` route from the earlier setup tutorial. Keep that route. In your project's root `urls.py`, add the account routes alongside it:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("pages.urls")),
]
```

Here `pages.urls` is the existing URL module that defines the named `home` view; use your own app's module if you named it differently. The account include supplies the `account_login`, `account_signup` and `account_logout` names used below. Defining a redirect setting alone does not create those routes.
    

## Database

You should finally be ready to run the migrations and create your database. If you recall we have avoided it in the previous tutorials.

Run `poetry run python manage.py makemigrations` and then run `poetry run python manage.py migrate`.

Django should create `users/0001_initial.py` with `CustomUser`, then apply the installed apps' migrations. The exact list varies by Django and allauth version. Run `poetry run python manage.py check` afterward; resolve errors before continuing.

Once this is done we will create a superuser, who would be able to log into the admin panel. Run `poetry run python manage.py createsuperuser` to create an admin that we can log in with to our admin dashboard. Choose a unique password that passes Django's validators, even for local development. If Django rejects it, choose another password rather than bypassing validation. See the [Django management command reference](https://docs.djangoproject.com/en/5.2/ref/django-admin/#createsuperuser).

Once the admin user is created run `poetry run python manage.py runserver` and head over to `http://127.0.0.1:8000/admin/` in your browser. Enter credentials you just created. If all is good congrats! If not, let me know.

Now, head over to `Sites`section and change it to `127.0.0.1` like so: ![django change site setting](https://res.cloudinary.com/built-with-django/image/upload/v1655567885/blog-images/django_change_site_setting_20220605004124_oo5bqn.png)

Now, we are done integrating `django-allauth` into our site. Now we just need to build Sign Up, Login, and Logout screens/logic.

## Authentication Screens

`django-allauth` takes care of signup and login screens for us. They will be very unstyled, but it will work. In future posts, we will focus on styling, but for this one, we will only care about functionality.

Add the following to `home.html` inside the content block:

```html
  {% if user.is_authenticated %}
	<p>Username: {{user.username}}</p>
	<p>Email: {{user.email}}</p>
	<a href="{% url 'account_logout' %}">Logout</a>
  {% else %}
	<a href="{% url 'account_login' %}">Login</a>
	<a href="{% url 'account_signup' %}">Signup</a>
  {% endif %}
```

We are telling our template engine to display links to `login` and `signup` pages if the user is not authenticated and display the username and email, as well as the logout screen if the user is authenticated.

And you're pretty much done.

Start the development server with `poetry run python manage.py runserver`. Open the signup link, create a test account, then test login and the logout confirmation screen. The logout link opens a confirmation page; it does not log the user out on GET. Django's [runserver documentation](https://docs.djangoproject.com/en/5.2/ref/django-admin/#runserver) covers this development-only command.

In the next post, we are going to integrate TailwindCSS into our app.