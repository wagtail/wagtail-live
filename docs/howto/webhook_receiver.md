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

We will take the example of Whatsapp to have concrete code to work on. But you can replace any occurence of Whatsapp with the input source you want to use.

### Define a webhook url

First, let's define the webhook url that the Whatsapp will use to send us new updates.

The base path of this url is `/wagtail_live/`.

We need to specify an extra path which is specific to Whatsapp.
To do so, we need to define the `url_path` and `url_name` attribute on our receiver like this:

```python
from wagtail_live.receivers.base import WebhookReceiverMixin

class WhatsappWebhookMixin(WebhookReceiverMixin):
    """Whatsapp webhook mixin."""

    url_path = "whatsapp/events/"
    url_name = "whatsapp_events_handler"
```

In this setup, the full path of our webhook url is `/wagtail_live/whatsapp/events/`.
The `url_name` attribute can be used for reversing purposes.

### Implement `set_webhook`

The next step is to implement the `set_webhook` **class** method.

The job of this method is to set a webhook connection with the input source.

This can be done programmatically (ex: Telegram) or manually (ex: Slack).

You have to check the input source docs to see how this can be done.

The relevant docs for Whatsapp can be found [here](https://developers.facebook.com/docs/whatsapp/api/webhooks).

According to the docs, we 
