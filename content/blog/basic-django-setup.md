---
id: 2
created: '2022-01-27 19:00:02.487000+00:00'
modified: '2022-08-05 19:35:20.796000+00:00'
title: Setting up a basic Django project with Poetry
slug: basic-django-setup
status: PB
description: In this tutorial, we will go through the process of setting up the most basic Django project with Poetry.
  We will use that as a setup up for other posts and tutorials.
unsplashID: OVbeSXRk_9E
icon: image/upload/v1659728681/blog-post-icon-prod/f6xe0hgl4vijlur6xp9w.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 4
  name: Poetry
  slug: poetry
- id: 5
  name: Pyenv
  slug: pyenv
author: 1
---
In this tutorial, we will go through the process of setting up the most basic Django project that we will be using for other posts and tutorials.

We will be using [Pyenv](https://github.com/pyenv/pyenv) and [Poetry](https://python-poetry.org/docs/) to manage the virtual environment and dependencies for your project.

Unfortunately, some things that I'm going through don't work exactly the same for Windows users (e.g. Pyenv). So, if you are following on a Windows machine you might run into some issues. If you do, try messaging me on Twitter, I'll try to do my best to help you.

During this tutorial, it might seem like too many things are going on things are becoming confusing. I'll try to separate it into manageable chunks that are easy to understand. And don't worry, some of the things in this tutorial only have to be done once.

The method of setting up repos that I propose can differ from others, but I really enjoy it. It helps me keep all the versions and virtual environments neat and tidy, which reduces the amount errors and bugs in the future. And if you stay with me till the end of the tutorial, hopefully, I can convert you to a Poetry person too :).

So, let's get the party started.

## Prerequisites

### Pyenv
- We are going to use brew to install Pyenv. If you don't have brew installed on your Mac, run the following command:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

- now let's install pyenv:
```bash
brew update
brew install pyenv
```

- If this didn't work for you try [these fixes](https://github.com/pyenv/pyenv#homebrew-in-macos).
- If you are on a Windows machine, follow the [following instruction](https://github.com/pyenv/pyenv#windows) to install pyenv.

- to test if this was installed correctly try running this in your terminal:
```bash
pyenv versions
```

- we are going to be using Python version 3.9.9 in our tutorial, so let's get that installed with the following command:
```bash
pyenv install 3.9.9
```

Your terminal will start giving you some outputs. Wait for a minute or two until the download and installation are complete. This is everything we are going to cover regarding pyenv, we don't need to know more for the purposes of this tutorial.

### Poetry
If you have Poetry installed you can skip this step.

So, let's first install Poetry.  You can do that by running the following command in your terminal:

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

If you are on Windows you would run the following in your Powershell:

```PowerShell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
```

The good news is that you have to do it once. To test that everything went smoothly, try running the following in your terminal:

```bash
poetry --version
```


## Setting up the Environment

Alright, we are now ready to start. Here is what you want to do:

- Open up your terminal, `cd` into the directory that you use to store all your code. For me it is: 
```bash
cd ~/code
```
- Then create a new directory for your project. I'm going to call mine "basic_django", but you can call it whatever else you want:
```bash
mkdir basic_django && cd basic_django
```
- Now, I suggest you open up your VS Code and open your newly-created directory. Alternatively, you can run this command in your terminal:
```bash
code .
```

- Let's use pyenv to explicitly say what Python version we will be using in that repo. For that, run the following in your terminal:
```bash
pyenv local 3.9.9
```
You should see a file named `.python-version` created in your folder. That's good.

- Now were are going to initialize Poetry project with:
```bash
poetry init
```

- You will be prompted to confirm a couple of settings. You can just skip the following:
```bash
Package name [basic_django]:
Version [0.1.0]:
Description []:
Author [Rasul Kireev <rasul.kireev@guycarp.com>, n to skip]:
License []:
```

- When you get to the following line type in "^3.8" and press Enter:
```bash
Compatible Python versions [^3.7]: ^3.9
```

The reason we do that is that the latest Django version requires the use of Python Version 3.8 and up.

- When you get to these prompts, type in "no". We are going to add our own dependencies later on:
```
Would you like to define your main dependencies interactively? (yes/no) [yes]

Would you like to define your development dependencies interactively? (yes/no) [yes]
```

- In the end, you would have gone through the process that looked something like this:

```toml
This command will guide you through creating your pyproject.toml config.

Package name [basic_django]:
Version [0.1.0]:
Description []:
Author [Rasul Kireev <rasul.kireev@guycarp.com>, n to skip]:
License []:
Compatible Python versions [^3.7]: ^3.9

Would you like to define your main dependencies interactively? (yes/no) [yes] no
Would you like to define your development dependencies interactively? (yes/no) [yes] no
Generated file

[tool.poetry]
name = "basic_django"
version = "0.1.0"
description = ""
authors = ["Rasul Kireev <rasul.kireev@guycarp.com>"]

[tool.poetry.dependencies]
python = "^3.7"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"


Do you confirm generation? (yes/no) [yes]
```

- Now let's add the Django dependency and try running the test server. So, to add a dependency in a Poetry project you just simply do:

```bash
poetry add Django
```

- After this command finished running let's see what we have. You should see two files:
	- `pyproject.toml`
	- `poetry.lock`

`poetry.lock` is a file that keeps all the project dependencies nice and constant so that if other people want to use your project, they will be able to install the exact same versions.

`pyproject.toml` is a nice visual file that lists all the project dependencies. In future posts, we will be using it to give our project configurations. Here is what we have in the `pyproject.toml` file right now (you should see something very similar):
```toml
[tool.poetry]
name = "basic_django"
version = "0.1.0"
description = ""
authors = ["Rasul Kireev <rasul.kireev@guycarp.com>"]

[tool.poetry.dependencies]
python = "^3.9"
Django = "^4.0.1"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

You can see that we are using the latest Django version, 4.0.1. If you want to use some other Django version, you can specify that when adding that dependency, like so:
```bash
poetry add "Django>=3.2.4"
```

If you want to change the version of the file retroactively, you can manually change the value in the `pyproject.toml` file and run:
```bash
poetry update
```

- Let's initiate a Django project with the Django admin command:
```bash
poetry run django-admin.py startproject basic_django .
```

- Ok, if you have never used poetry before this is important. In the command above can see I'm using `poetry run`. I'm adding this so that poetry runs the django-admin command for me from the virtual environment that will have all the dependencies that we specified earlier. If you don't want to keep typing `poetry run` for every command, you can simply run:
```bash
poetry shell
```
and then use commands as you usually would. However, I don't recommend that, since if you have multiple projects open, virtual environments might not work nicely with each other. I suggest explicitly running python commands with `poetry run …`.

- Second thing to note is the "." at the end of the command. This tells us that we have a parent directory already created, no need to do that for us.

- Now in your File Explorer you should have the following:
```
basic_django/ (This will be different for you)
manage.py      
poetry.lock    
pyproject.toml
```

- Finally to test that everything is set up as it should be let's run the local server:
```bash
poetry run python manage.py runserver
```

> Tip: you should not be writing these commands all the time. If you have already run one of these commands previously you can press the ⬆️ key on your keyboard, while in the terminal and it will show the previous command you run, so that you don't have to write it down again.

> Another tip: This is related. If you start typing "poetry run" in your terminal and then start pressing the ⬆️ key, your terminal will show only commands that have started with these keywords.

You will see something like this:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
January 27, 2022 - 17:25:15
Django version 4.0.1, using settings 'basic_django.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

This is good! We can go to our browser and go to the URL specified in the output (http://127.0.0.1:8000/)

- You should see a Django welcome screen.
- Notice the following line in the terminal output: "You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions." This is because we haven't run any migrations, and that's by design. We will not run any migrations until we have created a custom user model. If you don't anticipate your app to have a user, then don't worry about this.
- I did not yet write a guide on how to create a Custom User Model, so will refer you to the best resource I know and that is [Will Vincent's blog](https://learndjango.com/tutorials/django-custom-user-model)

## Adding Static Pages
Before we create models, databases, and other fun stuff let's first create some static pages. For that, we are going to create a "pages" application. I got this approach from Will Vincent, and have been using it for a long time.

- Create a new application with the following command:
```bash
poetry run python manage.py startapp pages
```
You should see a new folder pop up in your Code Editor named "pages" 👍.

- Head over to the `urls.py` file in the `basic_django` directory (remember for you the name of the "core" directory is different, whatever you chose when setting up the project) and add the following:
```python
# basic_django/urls.py
from django.contrib import admin
from django.urls import path, include # new

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("pages.urls")), # new
]
```
What we are doing here is we are adding a namespace to our site, basically saying that all the pages that will be created under the pages app will be at the root of the URL.

- Head over to the `setting.py` in the root folder (`basic_django` for me) and search for the TEMPLATES variable and replace the `DIRS` list to be this:
```python
# basic_django/settings.py
...
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.joinpath('templates'))], # new
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
...
```
This will tell our Django application that all templates are under the templates folder.

- Now, let's actually create the `templates` directory in the root folder. You can do that in the VS Code UI, or with the `mkdir` command. Just make sure that you are in the root folder.
- Inside the `templates` folder create a `base.html` file. Inside that html file add the following:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Basic Django Project</title>
</head>
<body>

  {% block content %}
  {% endblock %}

</body>
</html>
```
This template will be used as a base for all other templates in our project. Here, we can add the header, footer, and other components that will be present on each page of the site.

- Now, let's create a template for the home page. Create a `pages` folder, under `templates` folder. And inside that folder create a `home.html` file and add the following to it:
```html
{% extends 'base.html' %}

{% block content %}
  <h1>Helllloooooo!</h1>
{% endblock content %}
```
Here were are extending the base template and adding a header to it.

> Tip: If you are doing this for the first time, this might seem like a hard, long, and annoying task. But once you get the hang of it, things become to make sense and fall into their places.

Now the last two pieces to finish the proper setup of our Django project are URLs and Views.

- Let's start with views. Go to the `views.py` file under the `pages` folder and add the following code:
```python
# pages/views.py
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "pages/home.html"
```

- And let's create a URL for that HomeView. Create a `urls.py` in the `pages` folder and add the following:
```python
# pages/urls.py
from django.urls import path

from .views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]
```

- Now if you start the dev server with:
```bash
poetry run python manage.py runserver
```
you should see the word "Helllllooooo!".

## Conclusion

Congratulations! You are done with the Django Project Setup. After all of this you should have a directory looking something like this:
```
.
├── basic_django
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-39.pyc
│   │   ├── settings.cpython-39.pyc
│   │   ├── urls.cpython-39.pyc
│   │   └── wsgi.cpython-39.pyc
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── manage.py
├── pages
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-39.pyc
│   │   ├── urls.cpython-39.pyc
│   │   └── views.cpython-39.pyc
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── poetry.lock
├── pyproject.toml
└── templates
    ├── base.html
    └── pages
        └── home.html
```

After finishing this tutorial you should know how to set up a Django Project with Poetry and Pyenv. In the future, I'm going to be writing a guide on how to integrate various tools into your Django Project, and having this neat setup will help a lot.

If you run into any issues or have any questions, feel free to message me on [Twitter](https://twitter.com/builtwithdjango).