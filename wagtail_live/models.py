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
from django.utils.timezone import now
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

    def _get_live_post_index(self, live_post_id, low, high):

        while low < high:
            mid = (low + high) // 2
            curr_id = self.live_posts[mid].id

            if float(curr_id) == float(live_post_id):
                return mid

            elif float(curr_id) < float(live_post_id):
                low = mid + 1

            else:
                high = mid - 1

        return low

    def get_live_post_index(self, live_post_id):
        """Returns an existing livepost with live_post_id."""

        return self._get_live_post_index(live_post_id, 0, len(self.live_posts))

    def get_live_post_by_index(self, live_post_index):
        """Return a live post given its index in live_posts."""

        return self.live_posts[live_post_index]

    def get_live_post_by_id(self, live_post_id):
        live_post_index = self.get_live_post_index(live_post_id=live_post_id)
        return self.get_live_post_by_index(live_post_index)

    def add_block_to_live_post(self, block_type, block, live_block):
        live_block["content"].append((block_type, block))

    def add_live_post(self, live_post, live_post_id):
        if self.live_posts:
            lp_index = len(self.live_posts)
            while float(self.live_posts[lp_index - 1].id) > float(live_post_id):
                lp_index -= 1

            # Insert to keep posts sorted by time
            self.live_posts.insert(lp_index, ("live_post", live_post, live_post_id))

        else:
            self.live_posts.append(("live_post", live_post, live_post_id))

        self.last_update_at = now()
        self.save()

    def delete_live_post(self, live_post_id):
        live_post_index = self.get_live_post_index(live_post_id=live_post_id)
        del self.live_posts[live_post_index]
        self.last_update_at = now()
        self.save()

    def clear_live_post_content(self, live_post):
        live_post.value.get("content").clear()

    def update_live_post(self, live_post):
        live_post.value["modified"] = now()
        self.last_update_at = now()
        self.save()

    class Meta:
        abstract = True
