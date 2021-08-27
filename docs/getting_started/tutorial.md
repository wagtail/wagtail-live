# Wagtail Live Tutorial

This tutorial describes how to build a live blog with Wagtail Live.

## Install and run Wagtail Live

### Create and activate a virtual environment

We recommend using a virtual environment, which isolates installed dependencies from other projects.
This tutorial uses [`venv`](https://docs.python.org/3/tutorial/venv.html), which is packaged with Python 3.

Create a new virtual environment by running:

**On Windows** (cmd.exe):

```doscon
> python3 -m venv livesite\livesite
> livesite\livesite\Scripts\activate.bat
```

**On GNU/Linux or MacOS** (bash):

```console
$ python3 -m venv livesite/livesite
$ source livesite/livesite/bin/activate
```

For other shells see the [`venv` documentation](https://docs.python.org/3/library/venv.html).



### Install Wagtail Live and other dependencies

Use pip to install Wagtail and Wagtail Live:

```console
$ python -m pip install wagtail
$ python -m pip install wagtail-live
```

### Generate your site

Because the folder `livesite` was already created by `venv`, run `wagtail start` with an additional argument to specify the destination directory:

```console
$ wagtail start livesite livesite
```

### Create your first live page

Start a new `liveblog` app:

```console
$ cd livesite
$ python3 manage.py startapp liveblog
```

You will then need to add `wagtail_live` and `liveblog` to your `INSTALLED_APPS` in your `settings.base` file:
```python
    INSTALLED_APPS = [
        'home',
        'search',
        'liveblog',
        'wagtail_live',
        ...
        # Other apps
    ]
```

We can now create our first `LiveBlogPage`. Add the following in `liveblog.models`:
```python
    from wagtail.core.models import Page

    from wagtail_live.models import LivePageMixin

    class LiveBlogPage(Page, LivePageMixin):
        content_panels = Page.content_panels + LivePageMixin.panels
```



Create a `templates` folder inside your `liveblog` app. Add a `liveblog` folder in the `templates` folder that you just created and create a `live_blog_page.html` file. This represents our `LiveBlogPage` template.

For now, add this to your `live_blog_page.html` template:
```python
    {% include "wagtail_live/live_posts.html" %}
```
That's all we need in our models.

### Create the database

Let's create our tables now:

```console
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

### Create an admin user

```console
$ python3 manage.py createsuperuser
```

When logged into the admin site, a superuser has full permissions and is able to view/create/manage the database.

## Configure an input source and its corresponding receiver

We need an input source for our live blog.

An input source is a platform (often a messaging app, but any other tool that allows content editing and offers an API can be used) where we edit the content that appears on the front-end/client side.

We also need a receiver for our input source. The goal of a receiver is to receive/retrieve updates from an input source.

Choose an input source from the following list and configure its corresponding receiver:

- Slack: [Setup Slack Events API receiver](receivers/setup_slack.md)
- Telegram: [Setup Telegram webhook receiver](receivers/setup_telegram.md)

## Configuring a publisher

The last step required is to configure a publisher.

The goal of publishers is to "publish" new updates to the frontend/client side.

Choose and configure a publisher from the following list:

- Long Polling: [Set up long polling publisher](publishers/setup_long_polling.md)
- Interval Polling: [Set up interval polling publisher](publishers/setup_interval_polling.md)
- Django channels: [Set up Django channels publisher](publishers/setup_django_channels.md)
- PieSocket: [Set up PieSocket publisher](publishers/setup_piesocket.md)
- Websockets: [Set up websockets publisher](publishers/setup_websockets.md)
- Starlette: [Set up starlette publisher](publishers/setup_starlette.md)

That's it for the configuration part.

## Liveblogging

Go to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and create a new page of type `LiveBlogPage`.

You can choose the title you like for the page and fill the `channel_id` field with the ID of the channel you created in the input source chosen (Slack/Telegram).

Click on the `Live` button to display the page.

Enter in the channel you created in the input source chosen and start posting.

You should see your posts in the page momentarily!
