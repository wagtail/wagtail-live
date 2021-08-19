# How to write a webhook receiver

This guide shows how to add a receiver using the webhook technique.

First, we'll choose an input source to work with.

Then we'll subclass and implement the `WebhookReceiverMixin` class to handle webhook connections.

Finally we'll subclass and implement the `BaseMessageReceiver` class to process updates received from the input source chosen.

---

**Note:** You have to check the input source docs to implement most of the receiver's methods.

---

## Choose an input source

The input source is the main platform we use when publishing new content to our live blog. Therefore, we must first decide on the input source to use.

Some examples of possible input sources are [Facebook's Messenger Platform](https://developers.facebook.com/docs/messenger-platform), [Whatsapp](https://developers.facebook.com/docs/whatsapp), [Zulip](https://zulip.com/api/).

The only requirement is that it should allow setting up an outgoing webhook connection.

## Handle webhook connection

After choosing an input source, we need to handle webhook connections with it. 

The [`WebhookReceiverMixin`](../reference/receivers/webhook_receiver_mixin.md) is designed for that purpose. It makes the following assumptions:

- The input source sends new updates using POST requests,
- The input source expects to receive an HttpResponse `OK` after sending our site a new update.


### Define a `webhook url`

First, let's define the `webhook_url` that the input source uses to send us new updates.

The base path of this URL is `/wagtail_live/`. We need to specify an additional path parameter that is specific to an input source.

To do so, we need to define the `url_path` and `url_name` attribute on our receiver like this: (you will want to replace any occurrence of `input source` in this guide by the actual name of the input source.)

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

We can either do it programmatically (ex: Telegram, Whatsapp) or manually (ex: Slack).

For example, we can find the relevant docs for Whatsapp [here](https://developers.facebook.com/docs/whatsapp/api/webhooks).

If we set a webhook connection manually, meaning that there is no extra work to do, we can implement this method like this:
```python
class InputSourceWebhookMixin(WebhookReceiverMixin):
    # Previous code here

    @classmethod
    def set_webhook(cls):
        # Webhook connection is set manually.
        pass
```

On the other side, a typical way to set a webhook connection programmatically is to send a request to the input source's API with the `webhook url` defined previously and the updates we would like to receive.

The code should raise a `WebhookSetupError` exception if the process fails.

For example, here is the implementation of the `set_webhook` class method for the `TelegramWebhookMixin` (with extra comments for this guide):

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

The goal of this **class** method is to ensure, before running the server, that a webhook connection is set with the input source's API. 

It should return a boolean.

Similar to the `set_webhook` method, the implementation depends on whether we set a webhook connection manually or programmatically.

If we do it manually, we can simply return `True` and assume that a webhook connection is already set:

```python
@classmethod
def webhook_connection_set(cls):
    return True
```

For example, Telegram and Whatsapp provide the following endpoints, respectively, to get more information on the webhook status: `getWebhookInfo`, `/v1/settings/application`. We can then compare the Webhook URL received from the input source to our `webhook_url` to see if a webhook connection is already set or not.

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

Now that we can receive updates from the input source, we need to verify incoming requests.

To do so, we'll implement the `verify_request` method.

It should raise a `RequestVerificationError` if the incoming request can't be verified.

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

Telegram recommends using a secret path in the `webhook_url`, e.g. `https://www.example.com/token/`. Since nobody else knows our bot's token, if we receive a request to this endpoint with the correct token provided, we can be sure that it's from Telegram:

```python
def verify_request(self, request, body, token):
    if token != get_telegram_bot_token():
        raise RequestVerificationError
```

Whatsapp also recommends specifying a shared secret as a query parameter when setting the `webhook_url` to validate Webhook events. Example: `https://url?auth='[shared_secret]'`.


With our `InputSourceWebhookMixin` fully implemented, here is what happens when we receive an update from the input source:

1. Verify the request.
2. Dispatch the new event and process the updates received.
3. Acknowledge the request.

The next step is to implement an `InputSourceMessageReceiver` class that will process the updates received.


## Process updates

The `BaseMessageReceiver` proposes an interface to process updates received from an input source.

---

**Note:** You can click on any method listed in the **To-do**'s to see its documentation.

---

### Implement `dispatch_event`

The `dispatch_event` method is the 'entry point' to the `BaseMessageReceiver` class.

We will receive most updates when a message/post is added, edited, or deleted in the input source. Therefore, the first thing we will want to do when we receive a new update is finding its type i.e addition, edition or deletion. Then, we'll invoke the corresponding handler i.e `add_message`, `change_message` or `delete_message`.

For example, if an input source sends payloads like these:
```python
{
    "id": 1,
    "timestamp": 1234567,
    "type": "new_message",
    "content": "Some useful (or not) content."
},
{
    "id": 1,
    "timestamp": 12345678,
    "type": "edited_message",
    "content": "Some useful (or not) content edited."
},
{
    "id": 1,
    "timestamp": 123456789,
    "type": "deleted_message",
}
```

the `dispatch_event` method would look like:
```python
class InputSourceMessageReceiver(BaseMessageReceiver):
    def dispatch_event(self, event):
        event_type = event["type"]

        if event_type == "new_message":
            self.add_message(message=event)
            return
        elif event_type == "edited_message":
            self.change_message(message=event)
            return
        elif event_type == "deleted_message":
            self.delete_message(message=event)
            return
        else:
            # Handle other event types
```

---

**Tip:** In the early phases, you can add a line like this in the `dispatch_event` method:

```python
import json

class InputSourceMessageReceiver(BaseMessageReceiver):
    def dispatch_event(self, event):
        with open("input_source.json", mode="a") as f:
            f.write(json.dumps(event))

        # Rest of the code goes here  
```
You will have a good overview of the input source's API but also fixtures for tests!

---

### Handle a given message

The `add_message`, `change_message`, `delete_message` methods (already implemented) constitute the heart of the `BaseMessageReceiver` class.

They all work in a similar manner:

1. Retrieve the `channel_id` from the given message.

    **To-do:**

    - Implement [`get_channel_id_from_message`](../reference/receivers/base-message-receiver.md#wagtail_live.receivers.base.BaseMessageReceiver.get_channel_id_from_message) method.
    
2. Try to find the live page corresponding to `channel_id`.
    - If such a live page is found, go to step 3,
    - Else, return - the message has nowhere to be saved.

3. Retrieve the ID of the given message.

    **To-do:**

    - Implement [`get_message_id_from_message`](../reference/receivers/base-message-receiver.md#wagtail_live.receivers.base.BaseMessageReceiver.get_message_id_from_message) method.
    - Implement [`get_message_id_from_edited_message`](../reference/receivers/base-message-receiver.md#wagtail_live.receivers.base.BaseMessageReceiver.get_message_id_from_edited_message) method.

4. Create/retrieve/delete a post
    - If adding a new message/post: create a post corresponding to `message_id`;
    - If editing an old message/post: retrieve the post corresponding to `message_id`;
    - If deleting an old message/post: delete the post corresponding to `message_id`.
    - If adding or editing, go to step 5; 
    - if deleting, return.

5. Process text and files of the given message.

    A message/post is made of text and files (images).

    1. First, we retrieve the text and the files of the given message.

        **To-do:**

        - Implement [`get_message_text`](../reference/receivers/base-message-receiver.md#wagtail_live.receivers.base.BaseMessageReceiver.get_message_text) method.
        - Implement [`get_message_text_from_edited_message`](../reference/receivers/base-message-receiver.md#wagtail_live.receivers.base.BaseMessageReceiver.get_message_text_from_edited_message) method.
        - Implement [`get_message_files`](../reference/receivers/base-message-receiver.md#wagtail_live.receivers.base.BaseMessageReceiver.get_message_files) method.
        - Implement [`get_message_files_from_edited_message`](../reference/receivers/base-message-receiver.md#wagtail_live.receivers.base.BaseMessageReceiver.get_message_files_from_edited_message) method.
    
    2. Then do we process them.

        **To-do:**

        - Implement [`process_text`](../reference/receivers/base-message-receiver.md#wagtail_live.receivers.base.BaseMessageReceiver.process_text) method.
        - Implement [`process_files`](../reference/receivers/base-message-receiver.md#wagtail_live.receivers.base.BaseMessageReceiver.process_files) method.

6. Add/update the live post corresponding to the given message to/in live page.

## Wrap up

We can now define our `InputSourceWebhookReceiver` like this:

```python
class InputSourceWebhookReceiver(InputSourceWebhookMixin, InputSourceMessageReceiver):
    """A fully implemented receiver for input source."""

    pass
```

And to use it, we add it in our `settings`:
```python
WAGTAIL_LIVE_RECEIVER = "module_path.InputSourceWebhookReceiver"
```