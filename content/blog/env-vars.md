---
id: 11
created: '2024-08-06 08:39:55.810329+00:00'
modified: '2024-08-16 09:28:13.708382+00:00'
title: Setting up Environment Variables in Django
slug: env-vars
status: PB
description: In this tutorial, we are going to add support for environment variables in our app.
unsplashID: Led9c1SSNFo
icon: image/upload/v1722933596/blog-post-icon-prod/gmvwabnxdcbg99nhtrua.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 6
  name: git
  slug: git
- id: 7
  name: Github
  slug: github
author: 1
---
> Update (2024-10-16): add `overwrite=True` to `read_env` to make sure that your env variables are up to date.

## Introduction

In the previous tutorial we have covered the [installation of Stimulus.js](https://builtwithdjango.com/blog/stimulusjs) into our application.

Today, we are going to add support for environment variables. This is necessary to protect secret information from showing up in our git history.

This is important because there are bots scanning github for secrets that people can accidentally add to the repo.

For example, if you were to use ChatGPT API in your app you will need to authenticate using a secret key. If you add directly to the code a bot will be able to get that key and use it for their own good living you with a large bill.

You can read more about this in the [Config section of Twelve Factor App](https://12factor.net/config).

## Follow along

All the code in this tutorial will be in [this PR](https://github.com/builtwithdjango/basic-django/pull/5/files).

Before committing stuff to your repo, make sure that you have a `.gitignore` file in our repo. You can follow [this tutorial](https://builtwithdjango.com/blog/django-version-control) if you don't have one yet.

## Let's get to business

- In you project directory run `poetry add django-environ` to install the environment dependency.

- Create `.env` file to the root directory of your project.

- We are going to add 2 items to the environment for this exercise, debug mode and secret key.
   
```env
DEBUG=on

# Generate the key here: https://djecrety.ir/
SECRET_KEY="$wuy#b00i7rj="  # This is just an example, replace with your generated key. Make sure it is in quotes, otherwise there might be parsing issues.
```

- Add the following to `settings.py` file

```python
import environ  # new
import os  # new

env = environ.Env(
    DEBUG=(bool, False) # you can set defaults
)

BASE_DIR = ...  # old, don't touch

environ.Env.read_env(os.path.join(BASE_DIR, '.env'), overwrite=True)  # new, this needs to be after the BASE_DIR variable

# Replace DEBUG and SECRET_KEY with these
DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
```

- Start the server with `poetry run python manage.py runserver`. If it ran successfully then we are good.

Congrats, your Django app can now be safe.