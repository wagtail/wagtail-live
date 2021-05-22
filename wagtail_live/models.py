""" Wagtail Live models.

The LivePageMixin class embodies relevant properties to pages 
using Wagtail Live.

    Typical usage example:

    class LiveBlogPage(Page, LivePageMixin):
        category = models.CharField(max_length=255)

        content_panels = Page.content_panels + [
            FieldPanel('category'),
        ] + LivePageMixin.panels
"""

from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField

from .blocks import EmbedMessageBlock, ImageMessageBlock, TextMessageBlock


class LivePageMixin(models.Model):
    """A helper class for pages using Wagtail Live.

    Attributes:
        channel_name (str):
            Name of the corresponding channel in a messaging app.
        last_update_at (DateTime):
            Date and time of the last update for this channel/page.
        live_posts (StreamField):
            StreamField containing all the posts/messages published
            respectively on this page/channel.
    """

    channel_name = models.CharField(
        help_text="Channel name",
        max_length=255,
    )

    last_update_at = models.DateTimeField(
        help_text="Date and time of the last update for this channel/page",
        blank=True,
    )

    live_posts = StreamField(
        [
            ("text", TextMessageBlock()),
            ("image", ImageMessageBlock()),
            ("embed", EmbedMessageBlock()),
        ],
        blank=True,
    )

    panels = [
        FieldPanel("channel_name"),
        FieldPanel("last_update_at"),
        StreamFieldPanel("live_posts"),
    ]

    class Meta:
        abstract = True

