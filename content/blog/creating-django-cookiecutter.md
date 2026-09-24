---
id: 4
created: '2022-05-04 21:41:18.280000+00:00'
modified: '2022-08-05 19:34:10.900000+00:00'
title: How to Create a Django Cookiecutter from Scratch
slug: creating-django-cookiecutter
status: PB
description: In this tutorial I will show you how you can create your own Django Cookiecutter, which you will be
  able to reuse or share with others.
unsplashID: z8kriatLFdA
icon: image/upload/v1659728611/blog-post-icon-prod/jxauo4p1y1xdtr3pt5uz.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 8
  name: Python
  slug: python
- id: 9
  name: Cookiecutter
  slug: cookiecutter
author: 1
---
[Cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) is an awesome project created by [Audrey Roy Greenfeld](https://audrey.feldroy.com) and [Daniel Roy Greenfeld](https://daniel.feldroy.com) (I think) that let's you create a template from a Python package.

This is very cool, especially for people who create a lot of projects and/or have strong opinions on how things should be set up. 

Or if on other hand you don't like to think about setting up a repo you can use someone else's cookiecutter to jumpstart your project. For example [pydanny](https://github.com/pydanny)'s [cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django) is a popular way of creating new Django project. By using his template, you don't have to think about a lot of set up (User Authentication, Bootstrap Integration, Anymail, and a bunch of other neat things).

In this tutorial I will show you how you can create your own Django Cookiecutter, which you will be able to reuse or share with others. 

## Initial setup

- Make sure the `cookiecutter` library is installed.
```bash
pipx install cookiecutter
```

Note: if you don't have `pipx` installed, use `brew`:
```bash
brew install pipx
```

- Create a directory in which you will be working (that will essentially be [version controlled](https://builtwithdjango.com/blog/django-version-control))
   
```bash
mkdir bwd-django-cookiecutter && cd bwd-django-cookiecutter
```

- Install Django or update it if you have it installed.
```bash
python -m pip install Django --upgrade
```

- Start a new project:
```bash
django-admin startproject use_weird_name
```

**important note**
Use a unique and weird name. You can use something like `sdjhfaljkhd` for what it's worth. The reason for that is that we are going to use VS Code (or Code Editor of your choice) to replace this value with something else.

- Open the project in the code editor of your choice. If you use VS Code you can run this command:
```
code .
```

- Press `CMD+Shift+F` to start a global search. Search for the name of your project (in my case it would be `use_weird_name`) and replace it with `{{ cookiecutter.project_slug }}`. And just replace all the instances.

![vscode replace all](https://res.cloudinary.com/built-with-django/image/upload/v1651700011/blog-images/vscode_replace_all_20220504104257_mhksu2.png)

Also, don't forget to rename the two folders named `use_weird_name`. Global replace functionality doesn't apply to folder and file names, only contents.

- At the root of your project create a `cookiecutter.json` file. This is where you will specify any things that users (or yourself) can customize when creating a new project using your cookiecutter. For now, just add the following:

```json
/* cookiecutter.json */
{
  "project_name": "My Awesome Project",
  "project_slug": "{{ cookiecutter.project_name.lower()|replace(' ', '_')|replace('-', '_')|replace('.', '_')|trim() }}"
}
```

This will ask the user for the project name and will generate a project slug for them.

Nice job. We are almost done with the initial setup. Your current project should have the following structure:

```
.
├── cookiecutter.json
└── {{\ cookiecutter.project_slug\ }}
    ├── manage.py
    └── {{\ cookiecutter.project_slug\ }}
        ├── __init__.py
        ├── asgi.py
        ├── settings.py
        ├── urls.py
        └── wsgi.py
```

- This should be it for the most basic setup. Let's test if that works. Inside your terminal go into the same directory as your cookiecutter and run `cookiecutter bwd-django-cookiecutter/`. Don't forget to replace the `bwd-django-cookiecutter` part.
   
This is what I got:
![testing cookiecutter output](https://res.cloudinary.com/built-with-django/image/upload/v1651699916/blog-images/testing_cookiecutter_output_20220504111746_dwqml8.png)

Note that the slug has been "generated" automatically from the project name, but you can change it if you want.

Now let's run the test server:

```bash
python manage.py runserver
```

If you see this then your cookiecutter is doing everything correct.

```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
May 04, 2022 - 15:30:58
Django version 3.2.13, using settings 'testing_my_cookicutter.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## More abstractions

Once you have the initial setup ready you should be able to continue abstracting other parts of a Django application. Essentially anything that you think might change from user to user, or from project to project, should be abstracted. 

To get an inspiration / best practices on what can be abstracted check out [pydanny](https://daniel.feldroy.com)'s [django-cookiecutter repo](https://github.com/cookiecutter/cookiecutter-django) and the [cookiecutter.json file](https://github.com/cookiecutter/cookiecutter-django/blob/master/cookiecutter.json) specifically.

Let's do another one together.

I like to use Poetry to manage my projects so I'm going to add a `pyproject.toml` file with the `poetry init` command (if you are not sure how & why to use Poetry check out [this post](https://builtwithdjango.com/blog/basic-django-setup)).

Alright, so this is what I have done in the terminal (anything after → symbol is the command I used):

```bash
➜  bwd-django-cookiecutter cd \{\{\ cookiecutter.project_slug\ \}\} 
➜  {{ cookiecutter.project_slug }} ls
manage.py                       {{ cookiecutter.project_slug }}
➜  {{ cookiecutter.project_slug }} poetry init

This command will guide you through creating your pyproject.toml config.

Package name [{{ cookiecutter.project_slug }}]:  
Version [0.1.0]:  
Description []:  
Author [Rasul Kireev <rasul.kireev@guycarp.com>, n to skip]:  
License []:  
Compatible Python versions [^3.9]:  

Would you like to define your main dependencies interactively? (yes/no) [yes] no
Would you like to define your development dependencies interactively? (yes/no) [yes] no
Generated file

[tool.poetry]
name = "{{ cookiecutter.project_slug }}"
version = "0.1.0"
description = ""
authors = ["Rasul Kireev <rasul.kireev@guycarp.com>"]

[tool.poetry.dependencies]
python = "^3.9"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"


Do you confirm generation? (yes/no) [yes] 
➜  {{ cookiecutter.project_slug }} 
```

These commands generate a `pyproject.toml` file. Let's open it up and abstract some values!

This is what I have right now:

```toml
# {{ cookiecutter.project_slug }}/pyproject.toml
[tool.poetry]
name = "{{ cookiecutter.project_slug }}"
version = "0.1.0"
description = ""
authors = ["Rasul Kireev <rasul.kireev@guycarp.com>"]

[tool.poetry.dependencies]
python = "^3.9"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

As you can see, the name of the project has been done for us. But after some editing magic, this is what I'm going to end up with.

```toml
# {{ cookiecutter.project_slug }}/pyproject.toml
[tool.poetry]
name = "{{ cookiecutter.project_slug }}"
version = "0.1.0"
description = "{{ cookiecutter.project_description }}"
authors = ["{{ cookiecutter.author_name }} <{{ cookiecutter.author_email }}>"]

[tool.poetry.dependencies]
python = "^3.9"
Django = "^4.0.4"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

and I have also added a couple of lines to the `cookiecutter.json` file:

```json
/* cookiecutter.json */
{
  "project_name": "My Awesome Project",
  "project_slug": "{{ cookiecutter.project_name.lower()|replace(' ', '_')|replace('-', '_')|replace('.', '_')|trim() }}",
  "author_name": "Jane Doe", /* new */
  "author_email": "janedoe@example.com", /* new */
  "project_description": "" /* new */
}
```

## Conclusion

Now you know how to create your own Django cookiecutters (to learn more about it check out the [official docs](https://cookiecutter.readthedocs.io/en/latest/)). What you do with them is up to you. You can store them locally and use them to generate new projects, or you can version control them on Github and share them with others. Maybe someone will find it useful and will create it for their own projects. I would certainly opt for the latter.

For example, you can use [my cookiecutter](https://github.com/builtwithdjango/bwd-django-cookiecutter), by running this:

```bash
cookiecutter https://github.com/builtwithdjango/bwd-django-cookiecutter
```

If you do end up sharing it, make sure to add it to the [awesome cookiecutter repo](https://github.com/builtwithdjango/awesome-cookiecutters).

Fun fact: [Cory Zue](https://www.coryzue.com) is using cookiecutter for his [SaaS Pegasus](https://www.saaspegasus.com) project.