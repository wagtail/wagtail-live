# Input sources and receivers

Wagtail Live can receive messages from various input sources. Slack and Telegram are supported. An API and web application are in development.

Each input source has a receiver class. This class handles the incoming message, converts it to Streamfield blocks and stores it on the live blog page.

Not all input sources support all actions:

Action | Slack | Telegram
--- | --- | ---
Post message | ✅ | ✅
Update message | ✅ | ✅
Delete message | ✅ | ❌ <sup>1</sup>
Post image | ✅ | ✅
Update image | ✅ | ✅
Delete image | ✅ | ❌ <sup>2</sup>
Embed | ✅ | ✅
Emoji | ✅ | ✅

<sup>1,2</sup> Telegram does not call the webhook on delete.

!!! note
    In the Wagtail admin interface, you can edit messages. A message update is published to your live page automatically. A message update does not update the input source. Slack or Telegram still display the old message.
