# Set up long polling Publisher

This document describes how to set up a publisher using the long polling technique.

## Configure `WAGTAIL_LIVE_PUBLISHER`

In order to use the long polling technique for the publishing part, add this to your `settings`:
```python
WAGTAIL_LIVE_PUBLISHER = "wagtail_live.publishers.polling.LongPollingPublisher"
```

You can optionally set a polling timeout:
```python
WAGTAIL_LIVE_POLLING_TIMEOUT = value # in seconds
```
The default value is **60**(s).

## Add publisher template

We also need to add this to our `live_blog_page.html` template:
```python
{% include "wagtail_live/polling/long_polling.html" %}
```

Make sure you have these 2 lines in your template:
```python
{% include "wagtail_live/live_posts.html" %}

{% include "wagtail_live/polling/long_polling.html" %}
```
