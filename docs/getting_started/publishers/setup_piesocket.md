# Set up PieSocket publisher

---

!!! note
    PieSocket offers a 'free-plus' plan to Wagtail-live users. This is the same as the free plan, but with an increased limit of 1 million messages per day. To benefit from this offer, follow the partner link instead of the regular one.

---

This document describes how to set up a publisher using [PieSocket](https://www.piesocket.com/)([partner link](https://www.piesocket.com/?partner=2106)) websocket server API.

## Create a PieSocket account

First, you will need to create a PieSocket account [here](https://www.piesocket.com/pricing)([partner link](https://www.piesocket.com/pricing/?partner=2106)).

## Create a new API key

Once you have created an account, you will need to create a new **API KEY**.
In your dashboard, fill in the key name field and click the `CREATE NEW KEY` button.


![PieSocket dashboard screenshot](../../images/piesocket_dashboard.jpg)

## Retrieve your API key, your secret and PieSocket endpoint

Wagtail Live needs your `API_KEY` and your `SECRET`. It also needs the API endpoint to use.
After creating a new key, you can click the little information icon to find them as shown below:


![PieSocket credentials](../../images/piesocket_credentials.jpg)

### Add your credentials and PieSocket endpoint to `settings`

The PieSocket endpoint depends on the cluster. In the above image the PieSocket endpoint is: `us-nyc-1.piesocket.com/v3/`.

Add the following in your `settings.base` file:
```python
PIESOCKET_API_KEY = "your-api-key"
PIESOCKET_SECRET = "your-secret"
PIESOCKET_ENDPOINT = "your-piesocket-endpoint"
```

## Configure `WAGTAIL_LIVE_PUBLISHER`

In order to use PieSocket for the publishing part, add this to your `settings`:
```python
WAGTAIL_LIVE_PUBLISHER = "wagtail_live.publishers.piesocket.PieSocketPublisher"
```

## Add publisher template

We also need to add this to our `live_blog_page.html` template:
```python
{% include "wagtail_live/websocket/piesocket.html" %}
```
