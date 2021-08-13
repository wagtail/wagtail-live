# Settings

Wagtail Live makes use of the following settings, in addition to Django and Wagtail's settings:

## Synchronize live page with admin interface
### `WAGTAIL_LIVE_SYNC_WITH_ADMIN`
```python
WAGTAIL_LIVE_SYNC_WITH_ADMIN = False
```
This setting controls the synchronization of a live page when it's modified in the admin interface.

When `WAGTAIL_LIVE_SYNC_WITH_ADMIN` is `True` (default), the admin interface can be used as a way to publish instantly to a live page.

When `WAGTAIL_LIVE_SYNC_WITH_ADMIN` is `False`, changes made in the admin interface aren't automatically/live published. 

You can set the value of this setting to `False` if you don't intend to use the admin interface to publish/edit live posts. This will avoid making computations to track changes made in the admin interface.
