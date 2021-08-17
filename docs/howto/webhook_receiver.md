# How to write a webhook receiver

This guide shows how to add a receiver using the webhook technique.

## Choose an input source

The input source is the main platform you will use when publishing new content to your live blog. Therefore, you will first decide on the input source to use. 

Some examples of possible input source are: [Facebook's Messenger Platform](https://developers.facebook.com/docs/messenger-platform), [Whatsapp](https://developers.facebook.com/docs/whatsapp), [Zulip](https://zulip.com/api/)...

The only requirement is that the input source should allow setting up an outgoing webhook connection that they use to send relevant events (you will have specified) to your Wagtail site.

## Handle webhook connection

After choosing an input source, you need to handle webhook connections with it. The [`WebhookReceiverMixin`](../reference/receivers/webhook_receiver_mixin.md) is designed for that purpose. It makes the following assumptions about the input source:
- It sends new updates using POST requests
- It expects to receive an HttpResponse `OK` after sending our site a new update.


### Define a `webhook url`

First, let's define the `webhook url` that the input source will use to send us new updates.

The base path of this url is `/wagtail_live/`.

We need to specify an extra path which is specific to an input source.
To do so, we need to define the `url_path` and `url_name` attribute on our receiver like this: - you will want to replace any occurence of `input source` by the actual name of the input source. -

```python
from wagtail_live.receivers.base import WebhookReceiverMixin

class InputSourceWebhookMixin(WebhookReceiverMixin):
    """Input source webhook mixin."""

    url_path = "input_source/events/"
    url_name = "input_source_events_handler"
```

In this setup, the full path of our `webhook url` is `/wagtail_live/input_source/events/`.
The `url_name` attribute can be used for reversing/resolving purposes.

### Implement `set_webhook`

The next step is to implement the `set_webhook` **class** method.

The job of this method is to set a webhook connection with the input source.

This can be done programmatically (ex: Telegram, Whatsapp) or manually (ex: Slack).

You have to check the input source docs to see how this can be done.

For example, the relevant docs for Whatsapp can be found [here](https://developers.facebook.com/docs/whatsapp/api/webhooks).

If we set a webhook connection manually, meaning that there is no extra work to do, this method can be simply implemented like this:
```python
class InputSourceWebhookMixin(WebhookReceiverMixin):
    # Previous code here

    @classmethod
    def set_webhook(cls):
        # Webhook connection is set manually.
        pass
```

A typical way to set a webhook connection programatically is to send a request to the input source's API with the `webhook url` defined previously and the updates we would like to receive.

The code should raise a `WebhookSetupError` exception if the process fails.

For example, here is the implementation of the `set_webhook` class method for the `TelegramWebhookMixin` (with extra comments for the purpose of this guide):

```python
@classmethod
    def set_webhook(cls):
        # Send a request to https://api.telegram.org/bot-my-bot-token/setWebhook
        # to set a webhook connection.
        response = requests.get(
            get_base_telegram_url() + "setWebhook",
            params={
                # Specify our webhook url.
                "url": get_telegram_webhook_url(),

                # Specify updates we are interested in.
                "allowed_updates": [
                    "message",
                    "edited_message",
                    "channel_post",
                    "edited_channel_post",
                ],
            },
        )
        payload = response.json()

        # Check for errors.
        if not response.ok or not payload["ok"]:
            raise WebhookSetupError(
                "Failed to set Webhook connection with Telegram's API. "
                + f"{payload['description']}"
            )
```

### Implement `webhook_connection_set`

The goal of this **class** mathod is to ensure, before running the server, that a webhook connection is set with the input source's API so we don't miss events/updates. 

It should return a boolean.

Similarly to the `set_webhook` method, the implementation depends on whether a webhook connection is set manually or programatically.

If it's done manually, we can simply return `True` and assume that a webhook connection has already been set:

```python
@classmethod
def webhook_connection_set(cls):
    return True
```

Otherwise, you will have to check the input source docs to see how it's done.

For example, Telegram and Whatsapp provide the following endpoints respectively to get more informations on the webhook status: `getWebhookInfo`, `/v1/settings/application`. We can then compare the url received from the input source to our `webhook_url` to see if webhooh connection is already set.

The corresponding implementation for Telegram is:

```python
@classmethod
def webhook_connection_set(cls):
    response = requests.get(get_base_telegram_url() + "getWebhookInfo")
    if response.ok:
        # Ensure that the webhook is set with the correct URL
        payload = response.json()
        return (
            payload["ok"] and payload["result"]["url"] == get_telegram_webhook_url()
        )
    return False
```


### Verify incoming requests

Now that can receive updates from the input source, we need to verify incoming requests.
To do so, we'll implement the `verify_request` method. It should raise a `RequestVerificationError` if the incoming request can't be verified.

We must check the input source docs to see how it's done.

For example, Slack sends a timestamp and a signature on each request's headers. We can then compare those values with the current timestamp and the `SLACK_SIGNING_SECRET` to verify the request:
```python
def verify_request(self, request, body):
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    if not timestamp:
        raise RequestVerificationError(
            "X-Slack-Request-Timestamp not found in request's headers."
        )

    if abs(time.time() - float(timestamp)) > 60 * 5:
        # The request timestamp is more than five minutes from local time.
        # It could be a replay attack, so let's ignore it.
        raise RequestVerificationError(
            "The request timestamp is more than five minutes from local time."
        )

    sig_basestring = "v0:" + timestamp + ":" + body
    my_signature = "v0=" + self.sign_slack_request(content=sig_basestring)
    slack_signature = request.headers["X-Slack-Signature"]
    if not hmac.compare_digest(slack_signature, my_signature):
        raise RequestVerificationError("Slack signature couldn't be verified.")
```

Telegram recommends using a secret path in the `webhook_url`, e.g. https://www.example.com/<token>/. Since nobody else knows our bot's token, if we receive a request to this endpoint with the correct token provided, we can be sure that it's from Telegram:

```python
def verify_request(self, request, body, token):
    if token != get_telegram_bot_token():
        raise RequestVerificationError
```

Whatsapp also recommends specifying a shared secret as a query parameter when we set the `webhook_url` to validate Webhook events. Example: https://url?auth='[shared_secret]'.


With our `InputSourceWebhookMixin` fully implemented, we can now safely receive updates from the input source. The next step is to implement an `InputSourceMessageReceiver` class that will process the updates received.


## Process updates