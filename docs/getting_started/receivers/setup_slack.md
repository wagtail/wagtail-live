# Set up Slack Events API receiver

This document walks you through how to set up Slack as an input source for your live blog and use their `Events API` to receive new updates.

## Create a Slack app

First, you will need to [create a Slack app](https://api.slack.com/apps/new).
You may be prompted to create it from scratch or from an App Manifest. For the purpose of this tutorial, you can create your app from scratch.

Fill out your app name and pick a workspace to develop your app in. Click the `Create App` button and you should see your app's **Basic Information** page.


## Retrieve your tokens

Wagtail Live needs the following information to communicate with your app:

- `SLACK_SIGNING_SECRET`

    Slack signs all the requests it sends using a secret key.

    Wagtail Live needs that key to confirm that requests sent to the `wagtail_live/slack/events` endpoint come from Slack, by verifying their unique signature (you will learn more about this endpoint later).

    To find your secret key, go back to your app's page and navigate to the **Basic Information** section on the left sidebar. 

    Scroll down to **App Credentials** and you'll find your Signing Secret in the `SLACK_SIGNING_SECRET` field.

    Grab it and keep it in a safe place.


- `SLACK_BOT_TOKEN`

    You will need to provide this token to be able to download images from the Slack API.

    In your app's **Basic Information** page, navigate to the **OAuth & Permissions** on the left sidebar and scroll down to the **Bot Token Scopes** section. Click `Add an OAuth Scope`.

    - Add the `channels:history` scope.  
        This scope lets your app view messages and other content in **public channels** that your Slack app has been added to.
    - Add the `files:read` scope.  
        This scope gives your app the ability to read/download images in channels and conversations your Slack app has been added to

    Scroll up to the top of the **OAuth & Permissions** page and click `Install App to Workspace`. You’ll need to allow your app to be installed to your development workspace.

    Once you authorize the installation, you’ll get back to the **OAuth & Permissions** page and see a **Bot User OAuth Access Token** which starts with `xoxb-`.

    Grab the token and copy it somewhere. Keep your token safe!

### Add your tokens to `settings`

Add the following in your `settings.base` file:
```python
SLACK_SIGNING_SECRET = "your-signing-secret"
SLACK_BOT_TOKEN = "your-bot-token"
```

## Receiving Slack events

In order to receive events like when a message is sent in a channel, you need to hook a **Request URL** that Slack uses to send HTTP POST requests corresponding to events you specify. This URL needs to be publicly accessible. 

In the development phase, you will need a development proxy that creates a public URL and tunnels requests to your local server when you run `python3 manage.py runserver` in order to receive events from Slack.

If you are comfortable with ngrok, start ngrok on port 8000. Otherwise you can see how to [Set up a local web server with ngrok](setup_ngrok.md).

### Configure `SlackEventsAPIReceiver`

- Add the following to your `urls.py` file if not done yet:
    ```python
        from wagtail_live import urls as live_urls

        urlpatterns += [
            path('wagtail_live/', include(live_urls)),
        ]
    ```

- Add the following to your `settings` file:
    ```python
        WAGTAIL_LIVE_RECEIVER = "wagtail_live.receivers.slack.SlackEventsAPIReceiver"
    ```

- Make sure ngrok is running on port 8000 and start the development server in another shell like this:

    ```console
    $ python3 manage.py runserver
    ```

### Hook your request URL

Go back to your app's **Basic Information** page and look for **Event Subscriptions**. Toggle the `Enable events` button.

You'll be asked to type a **Request URL**. Get the URL generated by ngrok (the one that starts with https://) and append `/wagtail_live/slack/events` to it.

For example, if your generated URL is something like [https://abc.ngrok.io](), then the **Request URL** you should enter in Slack should be 
[https://abc.ngrok.io/wagtail_live/slack/events]().

As soon as you type the URL, Slack will send a POST request to verify it. Wagtail Live should handle this verification for you. 

You should see a green box indicating that your **Request URL** has been verified. From now on, Slack will send a POST request to [https://abc.ngrok.io/wagtail_live/slack/events]() whenever an event your bot has subscribed to occurs in Slack.

## Channel configuration

### Subscribe to Bot Events

After your request URL is verified, scroll down to **Subscribe to Bot Events** and click the `Add Bot User Event` button.

Choose the `message.channels` event and hit the `Save Changes` button. This allows your bot to listen for messages in **public channels** that it is added to. 

To listen for other types of messages/channels, see [this list](https://api.slack.com/scopes?filter=granular_bot&query=history) to check which scope you need to grant to your bot.

### Add your app to a channel

In the workspace where you installed the app, create a new channel.

In the channel's page, look for the `Show channel details` icon at the top right of the page and click it.

You will see another `More` dropdown button, click it and choose `Add apps`.

**Add your app to the channel.**

### Retrieve your channel's ID

To finish, you will need your channel's ID to create a page which will map to this channel in your live site.

To find the identifier of the channel you created, go to the channel's page, and grab the second identifier in the URL displayed on the address bar.

For example, if you go on your channel's page and the URL looks like [https://app.slack.com/client/T023G8L63FS/C024931MDK3](), then your channel identifier is **C024931MDK3**. 

You can then create a live page and add this identifier to the `channel_id` field of that page. From then, all messages changed/edited/deleted in the channel you created in Slack will be synced with your live page!
