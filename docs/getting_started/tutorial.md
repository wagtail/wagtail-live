# Wagtail Live Tutorial

This tutorial walks you through building a live blog with Wagtail Live.

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

> Wagtail Live isn't released yet. See Development docs to install it.

```console
$ pip install wagtail
$ pip install wagtail-live
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



Create a `templates` folder inside your `liveblog` app. Add a `liveblog` folder in the `templates` folder you just created and create a `live_blog_page.html` file. This represents our `LiveBlogPage` template.

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

An input source is a platform (often a messaging app but any other tool that allows content editing and offering an API can be used) where we edit the content that appears on the front-end/client side.

We also need a receiver for our input source. The goal of a receiver is to receive/retrieve updates from an input source.You can learn more about input sources and receivers here: [Input sources and receivers](../topics/input_source_and_receivers.md)


For this tutorial, we will use the live interface as an input source and configure its corresponding receiver.

### Add `wagtail_live_interface` to `INSTALLED_APPS`

`wagtail_live_interface` is automatically installed with `wagtail_live`.

You need to add it to your `INSTALLED_APPS` to use it.

In your `settings` file, add the following:
```python
    INSTALLED_APPS = [
        # Some apps
        ...
        'wagtail_live_interface',
        ...
        # Other apps
    ]
```

### Add `wagtail_live_interface` urls

In your `urls.py` file, add the following:
```python
    from wagtail_live_interface import urls as live_interface_urls

    urlpatterns += [
        path('wagtail_live_interface/', include(live_interface_urls)),
    ]
```

That's all we need to get the live interface working. To know if the live interface is properly set, run the following in a command line:
```console
$ python3 manage.py runserver
```
and head to [http://127.0.0.1:8000/wagtail_live_interface/channels/].

You should see this: (Add image)

You can create channels and inside channels you can post messages.

You can learn more about the live interface here:  
[Wagtail Live Interface: a lightweight web platform to manage content for live blogs powered by Wagtail Live](../topics/wagtail_live_interface.md)

## Configuring a publisher

The last step required is to configure a publisher.

The goal of publishers is to "publish" new updates to the frontend/client side. You can learn more about publishers here: [Publishers](../topics/publishers.md).

In this tutorial we will use the long polling technique to publish new updates on the frontend.

### Configure `WAGTAIL_LIVE_PUBLISHER`

In order to use the long polling technique for the publishing part, add this to your `settings`:
```python
WAGTAIL_LIVE_PUBLISHER = "wagtail_live.publishers.LongPollingPublisher"
```

You can optionally set a polling timeout by doing so:
```python
WAGTAIL_LIVE_POLLING_TIMEOUT = value # in seconds
```
The default value is **30**(s).

### Add publisher template

We also need to add this to our `live_blog_page.html` template:
```python
{% include "wagtail_live/polling/long_polling.html" %}
```

Make sure you have these 2 lines in your template:
```python
{% include "wagtail_live/live_posts.html" %}

{% include "wagtail_live/polling/long_polling.html" %}
```

That's it for the configuration part.

## Liveblogging

To start liveblogging, head to [http://127.0.0.1:8000/wagtail_live_interface/channels/]() and create a new channel named `test_channel` for example.

Now, go to [http://127.0.0.1:8000/admin/]() and create a new page of type `LiveBlogPage`.

You can choose the title you like for the page and fill the `channel_id` field with the name of the channel you created in the live interface, in our example `test_channel`.

Click on the `Live` button to display the page.

Enter in the channel you created in the live interface and start posting in the channel. You should see your posts in the page within few!