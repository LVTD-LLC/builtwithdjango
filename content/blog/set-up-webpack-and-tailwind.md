---
id: 6
created: '2022-06-24 21:40:59.227000+00:00'
modified: '2023-02-23 14:29:12.008000+00:00'
title: How to set up Webpack and TailwindCSS in a Django Project
slug: set-up-webpack-and-tailwind
status: PB
description: In this guide, we will set up Webpack and will install TailwindCSS into our Django application.
unsplashID: Nl-SXO4FAHw
icon: image/upload/v1659728521/blog-post-icon-prod/owqe1zfch0pdpknxegtx.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 11
  name: Frontend
  slug: frontend
- id: 12
  name: Webpack
  slug: webpack
- id: 13
  name: TailwindCSS
  slug: tailwindcss
author: 1
---
> Update: Thanks to Jeffrey Hagenstein for reporting a bug in this tutorial. I forgot to mention the addition of `STATIC_ROOT = BASE_DIR.joinpath('static')` to `settings.py` to make sure that collectstatic works as intended.

In this guide, we will set up [Webpack](https://webpack.js.org/) and will install [Tailwind](https://tailwindcss.com/) into our Django application.

The process might seem complicated at first, but once you are done with the setup you won't have to do this again, ever. So, buckle up, and let's go.

## Webpack Boilerplate

[Michael Yin](https://github.com/michael-yin/) built a neat boilerplate for webpack configuration. We are going to use that to jumpstart our work with the frontend.

So, first, we are going to install `python-webpack-boilerplate` with `poetry add python-webpack-boilerplate`.

Once the dependency is added, add `webpack_boilerplate` to `INSTALLED_APPS` in `settings.py`, like so:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "webpack_boilerplate", # new
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "pages.apps.PagesConfig",
    "users.apps.UsersConfig",
]
```

Please note that the last five apps we added in the [last Authentication tutorial](https://builtwithdjango.com/blog/user-authentication).

After you modified INSTALLED_APPS, run `poetry run python manage.py webpack_init` to generate all the required settings. You will be asked for some input. Here is what I recommend:

```
➜  basic-django git:(main) ✗ poetry run python manage.py webpack_init
project_slug [frontend]: 
run_npm_command_at_root [n]: y
 [SUCCESS]: Frontend app 'frontend' has been created. To know more, check https://python-webpack-boilerplate.rtfd.io/en/latest/frontend/
```

You will see a bunch of files generated:

- `.babelrc`
- `.browserslistrc`
- `.eslintrc`
- `.nvmrc`
- `.stylelintrc.json`
- `package-lock.json`
- `package.json`
- `postcss.config.js`

and one directory `frontend`.

Go to `package.json` and modify some fields. Modify the following:

- name
- description
- repo url (if there is one, otherwise just remove the whole "repository" object)
- bugs url (if there is one, otherwise just remove the whole "bugs" object)

This step above is not necessary, but it is certainly good to have to make sure all the info about the project is correct.

Now run `npm install` to install all npm libraries. 

> If you can't run npm, make sure you have nodejs installed. I recommend [Tania Rascia's guide](https://www.taniarascia.com/setting-up-a-brand-new-mac-for-development/#nodejs) for that. I also recommend installing the Latest Stable Version (LTS) of Nodejs, which you can check on [nodejs](https://nodejs.org/en/) site.

## Live Reload (Optional, but Recommended)

There is an awesome side benefit of setting up Tailwind via webpack and is Hot Reloading. If you don't know what Hot Reloading is then you are in for a treat. 

Essentially every time you make changes to any python or html file, the development server will reload automatically, which means you don't have to go to the browser and reload the page.

So, to do that, head over to `webpack.config.dev.js` under the `frontend/webpack` folder and modify the following parts:

- remove `hot: true,` line
- and add `watchFiles` to the `devServer` object

So, your devServer object will look something like that:

```JavaScript
	devServer: {
	  host: "0.0.0.0",
	  port: 9091,
	  headers: {
	    "Access-Control-Allow-Origin": "*",
	  },
	  devMiddleware: {
	    writeToDisk: true,
	  },
	  watchFiles: [
	    Path.join(__dirname, '../../**/*.py'),
	    Path.join(__dirname, '../../templates/**/*.html'),
	  ],
	}
```

Or you can just copy the whole file from [this gist](https://gist.github.com/rasulkireev/a186d2d9af397184f7cf8b987566eb18) and paste over the current content. 

That's it!

## TailwindCSS

Alright, let's actually install [TailwindCSS](https://tailwindcss.com/).

[Recommended way](https://tailwindcss.com/docs/using-with-preprocessors) to install tailwind is with the use of preprocessors like `postcss`, so that's what we are going to do.

Run `npm install -D tailwindcss@latest postcss postcss-import` and then run `npm install autoprefixer@10.4.5 --save-exact`. The reason for that is that newer versions of `autoprefixer` give an irrelevant warning when compiling, so we want to pinpoint version 10.4.5.

After the installation is complete, add the following to `postcss.config.js`:

```javascript
module.exports = {
  plugins: {
    'postcss-import': {},
    'tailwindcss/nesting': 'postcss-nesting',
    tailwindcss: {},
    autoprefixer: {},
    'postcss-preset-env': {
      features: { 'nesting-rules': false },
    },
    ...(process.env.NODE_ENV === 'production' ? { cssnano: {} } : {})
  }
}
```

I'm no webpack expert, so I won't be able to give you detailed info on each setting. I am following official Tailwind docs. This setup worked perfectly for me.

Now let's set add some `tailwindcss` settings.

> Optional (but recommended): Install two `tailwindcss` plugin with `npm install -D @tailwindcss/typography @tailwindcss/forms`. These are not required but are very useful. There is no downside to installing these. So, just, please… 😄

Run `npx tailwindcss init` to generate `tailwind.config.js` file and add the following to the file:

```javascript
module.exports = {
  content: [
    './templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}
```

Here we are telling tailwind where our html is so that it can parse the files add only generate the required classes. This will keep prod files as small as possible.

Now let's create the CSS file. If you look under the following path `frontend/src/styles` you will see an `index.scss` file. Rename it to `index.css` instead. If you like to use SCSS, you can keep it as is.

Replace the content of that file with the following:
```css
@import "tailwindcss/base"; 
@import "tailwindcss/components"; 
@import "tailwindcss/utilities";
```

I swear we are almost done!

Under `frontend/src/application` you'll see two `.js` files: `app.js` and `app2.js`. Rename the `app.js` file to `index.js`, for consistency's sake, and then replace the content of the `index.js` with the following:

```JavaScript
import "../styles/index.css";
```

> Feel free to delete the `app2.js` file as we won't need it now or in the future.

Let's test everything is working by running `npm run start`. Give it a second to compile. If you see something like this then you are good to go:

```
➜  basic-django git:(main) ✗ npm run start                               

> python-webpack-boilerplate@1.0.0 start
> webpack serve --config frontend/webpack/webpack.config.dev.js

<i> [webpack-dev-server] Project is running at:
<i> [webpack-dev-server] Loopback: http://localhost:9091/
<i> [webpack-dev-server] On Your Network (IPv4): http://192.168.0.116:9091/
<i> [webpack-dev-server] On Your Network (IPv6): http://[fe80::1]:9091/
<i> [webpack-dev-server] Content not from webpack is served from

...

orphan modules 27.8 KiB [orphan] 8 modules
cacheable modules 168 KiB (javascript) 16.3 KiB (css/mini-extract)
  modules by path ./node_modules/ 167 KiB
    modules by path ./node_modules/webpack-dev-server/client/ 56.8 KiB 12 modules
    modules by path ./node_modules/webpack/hot/*.js 4.3 KiB 4 modules
    modules by path ./node_modules/html-entities/lib/*.js 81.3 KiB 4 modules
    modules by path ./node_modules/mini-css-extract-plugin/dist/hmr/*.js 5.97 KiB 2 modules
    + 2 modules
  modules by path ./frontend/src/ 621 bytes (javascript) 16.3 KiB (css/mini-extract)
    modules by path ./frontend/src/application/*.js 252 bytes 2 modules
    modules by path ./frontend/src/styles/*.css 329 bytes (javascript) 16.3 KiB (css/mini-extract) 2 modules
    ./frontend/src/components/sidebar.js 40 bytes [built] [code generated]
webpack 5.70.0 compiled successfully in 4194 ms
```

If not, feel free to send me an email with your error, and I'll help you get it solved. Now, press Ctrl+C to stop the server of the frontend files, and let's continue.

## Integrating into Django

This is the last step in our setup. All we need to do now is make Django templates load all the javascript and CSS files. Head over to `settings.py` and add the following:

```python
STATICFILES_DIRS = [
    BASE_DIR.joinpath("frontend/build"),
]

STATIC_ROOT = BASE_DIR.joinpath('static')

WEBPACK_LOADER = {
    "MANIFEST_FILE": BASE_DIR.joinpath("frontend/build/manifest.json"),
}
```

Then head over to `base.html` file and add the following:
```html
{% load webpack_loader static %} <!-- new -->

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Basic Django Project</title>

  {% stylesheet_pack 'index' %} <!-- new, referring to index.css --> 
  {% javascript_pack 'index' attrs='defer' %} <!-- new, referring to index.js -->
</head>
<body>

  {% block content %}
  {% endblock %}

</body>
</html>
```

That's it for our setup. Let's now actually test if it works. Head over to `home.html` and add some tailwind classes, for example:
```html
{% extends 'base.html' %}

{% block content %}
  <h1 class="text-green-800 text-lg">Helllloooooo!</h1> <!-- new -->

  ... other stuff ...	
{% endblock content %}
```

Now, let's start both the frontend and the backend. In your Terminal start the frontend with `npm run start`, then open a new terminal in VS Code with Ctrl+N. 

In that new terminal window first, run `poetry run python manage.py collectstatic`, then start the Django server there with `poetry run python manage.py runserver`. Head over to `http://127.0.0.1:8000/`.

You should see the styling changes being applied. Now is a good chance to also test the hot reloading. Try modifying the `home.html` file and saving it. Changes should automatically get applied to the page.

Now you are free to do any changes to the page styles and they will automatically get parsed and re-rendered. Congrats!

This wraps up our guide on integrating Webpack and TailwindCSS.