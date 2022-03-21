# Hooks

Wagtail Live makes use of the following hooks:

# `process_livepost_before_add`

This hook allows to perform additional processing of a live post before it's added to a live page.

A function using this hook must accept the live post being processed and the message received from the input source as arguments.

A typical use-case of this hook is to set values for extra fields defined on a custom live post block class definition.

For example, if we define a custom live post block as follows:

```python
from wagtail.snippets.blocks import SnippetChooserBlock

from wagtail_live.blocks import LivePostBlock


class MyCustomLivePostBlock(LivePostBlock):
    posted_by = SnippetChooserBlock("my_app.MyUserModel", required=False)
```

and specify it in our settings as the live post block to use;

```python
WAGTAIL_LIVE_POST_BLOCK="my_app.blocks.MyCustomLivePostBlock"
```

We can use this hook to set the `posted_by` field's value of a live post before it's added:

```python
from wagtail.core import hooks

from my_app.models import MyUserModel

@hooks.register("process_livepost_before_add")
def set_posted_by(live_post, message):
    live_post["posted_by"] = MyUserModel.objects.get_or_create(username=message["user"])
```
