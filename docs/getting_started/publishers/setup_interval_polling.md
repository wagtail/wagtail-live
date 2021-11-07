# Set up interval polling Publisher

This document describes how to set up a publisher using the interval polling technique.

## Configure `WAGTAIL_LIVE_PUBLISHER`

In order to use the interval polling technique for the publishing part, add this to your `settings`:
```python
WAGTAIL_LIVE_PUBLISHER = "wagtail_live.publishers.polling.IntervalPollingPublisher"
```

You can optionally set a polling interval:
```python
WAGTAIL_LIVE_POLLING_INTERVAL = value # in milliseconds
```
The default value is **3000**(ms).

## Add publisher template

We also need to add this to our `live_blog_page.html` template:
```python
{% include "wagtail_live/polling/interval_polling.html" %}
```

Make sure you have these 2 lines in your template:
```python
{% include "wagtail_live/live_posts.html" %}

{% include "wagtail_live/polling/interval_polling.html" %}
```

## Add URLs

Add the Wagtail Live URLs to your `urls.py`:

```python
from django.urls import include, path
from wagtail_live import urls as live_urls

urlpatterns += [
    path('wagtail_live/', include(live_urls)),
]
```
