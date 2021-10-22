# Settings

Wagtail Live makes use of the following settings, in addition to Django's and Wagtail's:

## Core
### `WAGTAIL_LIVE_PAGE_MODEL`
| Description                                                                              | Required | Default |
|------------------------------------------------------------------------------------------|----------|---------|
| Path to the page model to use. <br>The page specified must inherit from `LivePageMixin`. | Yes      | None    |

Example:
```python
WAGTAIL_LIVE_PAGE_MODEL = "liveblog.models.LiveBlogPage"
```

### `WAGTAIL_LIVE_RECEIVER`
| Description                                                                                      | Required | Default |
|--------------------------------------------------------------------------------------------------|----------|---------|
| Path to the receiver to use. <br>The receiver specified must inherit from `BaseMessageReceiver`. | Yes      | None    |

See [Configure an input source and its corresponding receiver](../getting_started/tutorial.md#configure-an-input-source-and-its-corresponding-receiver).


### `WAGTAIL_LIVE_PUBLISHER`
| Description                   | Required | Default |
|-------------------------------|----------|---------|
| Path to the publisher to use. | Yes      | None    |

See [Configuring a publisher](../getting_started/tutorial.md#configuring-a-publisher).

## Slack receivers
### `SLACK_SIGNING_SECRET`
| Description          | Required            | Default |
|----------------------|---------------------|---------|
| Slack signing secret | For Slack receivers | None    |


### `SLACK_BOT_TOKEN`
| Description                                                   | Required            | Default |
|---------------------------------------------------------------|---------------------|---------|
| Slack bot token. This is used to download images from the Slack API. | For Slack receivers | None    |

## Telegram receivers
### `TELEGRAM_BOT_TOKEN`
| Description        | Required               | Default |
|--------------------|------------------------|---------|
| Telegram bot token | For Telegram receivers | None    |

### `TELEGRAM_WEBHOOK_URL`
| Description                                                                                                           | Required               | Default |
|-----------------------------------------------------------------------------------------------------------------------|------------------------|---------|
| The URL used by Telegram to send updates to your app.<br>It must be publicly accessible and served over `https`. | For Telegram receivers | None    |

## Polling publishers
### `WAGTAIL_LIVE_POLLING_TIMEOUT`
| Description                                                 | Required | Default |
|-------------------------------------------------------------|----------|---------|
| Polling timeout (in seconds) for the `LongPollingPublisher` | No       | 60(s)   |

### `WAGTAIL_LIVE_POLLING_INTERVAL`
| Description                                                           | Required | Default  |
|-----------------------------------------------------------------------|----------|----------|
| Polling interval (in milliseconds) for the `IntervalPollingPublisher` | No       | 3000(ms) |

## Websocket publishers
### `WAGTAIL_LIVE_REDIS_URL`
| Description      | Required | Default                  |
|------------------|----------|--------------------------|
| Redis server URL | No       | redis://127.0.0.1:6379/1 |

### `WAGTAIL_LIVE_SERVER_HOST`
| Description                                                            | Required | Default   |
|------------------------------------------------------------------------|----------|-----------|
| Server host for websocket publishers based on starlette, websockets... | No       | localhost |

### `WAGTAIL_LIVE_SERVER_PORT`
| Description                                                            | Required | Default |
|------------------------------------------------------------------------|----------|---------|
| Server port for websocket publishers based on starlette, websockets... | No       | 8765    |

## Synchronize live page with admin interface
### `WAGTAIL_LIVE_SYNC_WITH_ADMIN`
| Description                                                                                             | Required | Default |
|---------------------------------------------------------------------------------------------------------|----------|---------|
| This setting controls the synchronization of a live page <br>when it's modified in the admin interface. | No       | True    |

When `WAGTAIL_LIVE_SYNC_WITH_ADMIN` is `True` (default), the admin interface can be used as a way to publish instantly to a live page.

When it's `False`, changes made in the admin interface aren't automatically/live published. 

You can set the value of this setting to `False` if you don't intend to use the admin interface to publish/edit live posts. This will avoid making computations to track changes made in the admin interface.
