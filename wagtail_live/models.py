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

from functools import lru_cache

from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField

from .blocks import LivePostBlock


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
        null=True,
        blank=True,
    )

    live_posts = StreamField(
        [
            ("live_post", LivePostBlock()),
        ],
        blank=True,
    )

    panels = [
        FieldPanel("channel_name"),
        FieldPanel("last_update_at"),
        StreamFieldPanel("live_posts"),
    ]

    @lru_cache(maxsize=1)
    def get_posts_by_id_index_pair(self, last_update_at):
        """Returns a dict that maps a post id to its index in live_posts.
        
        Not sure if the implementation is right, but the idea is that
        we don't need to recompute this value if there is not a new message.
        Editing a message doesn't affect the mapping msg_id-index but deleting does. 
        So keep track of last_update.
        """

        return {msg.id: index for index, msg in enumerate(self.live_posts)}

    def get_live_post_index(self, live_post_id):
        """Returns an existing livepost with live_post_id."""

        posts_by_id_index_pair = self.get_posts_by_id_index_pair(self.last_update_at)
        return posts_by_id_index_pair[live_post_id]

    def get_live_post(self, live_post_index):
        """Return a live post given its index in live_posts."""

        return self.live_posts[live_post_index]

    class Meta:
        abstract = True
