# Wagtail Live - Slack tutorial

This tutorial walks you through building a live blog with Wagtail Live and Slack.

## Before you start

### Create a Slack app

First, you will need to create [a Slack app](https://api.slack.com/apps/new).
You may be prompted to create it from scratch or from an App Manifest. For the purpose of
this tutorial, you can create your app from scratch.

Fill out your app name and pick a workspace to develop your app in.
Click the `Create App` button and you should see your app's **Basic Information** page.

### Retrieve your tokens

Wagtail Live needs the following information to communicate with your app:

- `SLACK_SIGNING_SECRET`

    Slack signs the requests it sends using this secret. We need it in order to confirm that each 
    request comes from Slack by verifying its unique signature.

    Go back to your app's page and navigate to the **Basic Information** section on the left sidebar.
    Scroll down to **App Credentials**. You'll find there your Signing Secret. Grab it and keep it in a safe
    place too.

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

**For other shells** see the [`venv` documentation](https://docs.python.org/3/library/venv.html).

### Save tokens

Let's save the signing secret as an environment variable like this:

**On Windows** (cmd.exe):

```doscon
> SET SLACK_SIGNING_SECRET=<your-signing-secret>
```

**On GNU/Linux or MacOS** (bash):

```console
$ export SLACK_SIGNING_SECRET=<your-signing-secret>
```

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

    INSTALLED_APPS = [
        'home',
        'search',
        'liveblog',
        'wagtail_live',
        ...
        # Other apps
    ]

We can now create our first `LiveBlogPage`. Add the following in `liveblog.models`:
```
    from wagtail.core.models import Page

    from wagtail_live.models import LivePageMixin

    class LiveBlogPage(Page, LivePageMixin):
        content_panels = Page.content_panels + LivePageMixin.panels
```



Create a `templates` folder inside your `liveblog` app. Add a `liveblog` folder in the `templates` folder
you just created and create a `live_blog_page.html` file. This respresents our `LiveBlogPage` template.
For now, add this to your `live_blog_page.html` template:
```
    {{ self.live_posts }}
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

Before firing up the server, we need additional setup to listen to Slack events.

### Add tokens to `settings`

Add the following in your `settings.base` file:
```
    # Wagtail Live settings

    SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
    WAGTAIL_LIVE_PAGE_MODEL = "liveblog.models.LiveBlogPage"
```

## Listening to Slack events

In order to receive events like when a message is sent in a channel, we need to hook a **Request URL** that
Slack uses to send HTTP POST requests corresponding to events we specify.
This URL needs to be publicly accessible. However, running `./manage.py runserver` only provide us a locally
accessible URL. We use a development proxy (ngrok) that will create a public URL and tunnel requests to our own 
development environment. 

### Setting up ngrok

1. Head to [ngrok](https://ngrok.com/) and download the version that corresponds to your platform.
2. To install it, we need to extract the file into a folder and run ngrok from there.
    You can extract it into the folder of your preference. In that configuration, you will
    need to navigate to the folder where you unzipped ngrok whenever you want to start ngrok.
    If you want to run ngrok from any path on the command line, you will have to extract the ngrok file
    on your system's `$PATH` directory.

    To get your system's `$PATH`, type from the command line:
    ```console
    $ echo $PATH
    ```
3. Start ngrok server
    if ngrok is on your `$PATH`, type:
    ```console
    $ ngrok http 8000
    ```

    If the above doesn't work or you extracted ngrok in another directory, navigate to
    that directory and type:
    ```console
    $ ./ngrok http 8000
    ```

    If all goes well, you should see a generated URL that you can use (Slack recommend the one that starts with https://). This URL will be the base of our request URL.

    We can now register a public-facing URL for our app that tunnels to our local server.

### Request URL verification

In your `urls.py` file, add the following:
```
    from wagtail_live import urls as live_urls


    urlpatterns += [
        path('wagtail_live/', include(live_urls)),
    ]
```

Now we can start the server. Make sure ngrok is running on port 8000.
Type:

```console
$ python3 manage.py runserver
```

Search for **Event Subscriptions** on your app's **Basic Information** page and toggle the `Enable events` button.
You'll be asked to type a **Request URL**. Get the generated URL by ngrok (the one that that starts with https://)
and append `/wagtail_live/slack/events` to it. 
For example, if your generated URL is something like https://e54acd3a20b3.ngrok.io, then the **Request URL** you
should enter in Slack should be 
https://e54acd3a20b3.ngrok.io/wagtail_live/slack/events.

As soon as you type the URL, Slack will send a POST request to verify the URL given with a challenge parameter.
You don't have to bother about it, Wagtail Live handles it.

### Channel configuration

After your request URL is verified, scroll down to **Subscribe to Bot Events** and click the `Add Bot User Event` button.
Choose the `message.channels` event and hit the `Save Changes` button. This allow your bot to listen for messages in **public channels** that it is added to.

In the workspace you installed the app, create a new channel.
In the channel's page, look for the `Show channel details` icon at the top right of the page and click it.
You will see another `More` dropdown button, click it and choose `Add apps`.

Add your app to the channel.

Head to http://127.0.0.1:8000/admin/ and log in with the superuser credentials you created.

Create a new Live Blog Page with the title of your preference. To know the identifier of the channel you created,
you can simply go to the channel page, and grab the second identifier in the URL displayed on the adress bar.

For example, if you go on your channel's page and the URL looks like https://app.slack.com/client/T023G8L63FS/C024931MDK3,
then your channel identifier is **C024931MDK3**. 

Add this identifier to the channel name field in your Live Blog Page.

From now on, all messages changed/edited/deleted will be synced with your live blog page!
