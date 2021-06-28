""" Wagtail Live models."""
from typing import Optional

from django.db import models
from django.utils.timezone import now
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField

from .blocks import LivePostBlock


class LivePageMixin(models.Model):
    """A helper class for pages using Wagtail Live.
    Attributes:
        channel_id (str):
            Id of the corresponding channel in a messaging app.
        live_posts (StreamField):
            StreamField containing all the posts/messages published
            respectively on this page/channel.
    """

    channel_id = models.CharField(
        help_text="Channel ID",
        max_length=255,
        blank=True,
    )

    live_posts = StreamField(
        [
            ("live_post", LivePostBlock()),
        ],
        blank=True,
    )

    panels = [
        FieldPanel("channel_id"),
        StreamFieldPanel("live_posts"),
    ]

    def _get_live_post_index(self, message_id: str) -> Optional[int]:
        """Retrieves the index of a live post.
        Searches backwards.

        Args:
            message_id (str):
                ID of the message corresponding to a live post.

        Returns:
            (int) Index of the live post if found else None
        """

        posts = self.live_posts
        index = len(posts) - 1

        while index >= 0:
            if posts[index].value["message_id"] == message_id:
                break

            index -= 1

        return index if index >= 0 else None

    def get_live_post_index(self, message_id: str) -> Optional[int]:
        """Retrieves index of a livepost."""

        return self._get_live_post_index(message_id=message_id)

    def get_live_post_by_index(self, live_post_index: int) -> LivePostBlock:
        """Retrieves a live post by its index.

        Args:
            live_post_index (str): Index of the live post to look for.

        Returns:
            (LivePostBlock) The live post instance

        Raises:
            (IndexError) if a live post with the given index doesn't exist.
        """

        return self.live_posts[live_post_index]

    def get_live_post_by_message_id(self, message_id: str) -> LivePostBlock:
        """Retrieves a live post by its ID.

        Args:
            message_id (str):
                ID of the message corresponding to a live post.

        Returns:
            (LivePostBlock) The live post instance

        Raises:
            (KeyError) if a live post with the given ID doesn't exist.
        """

        live_post_index = self.get_live_post_index(message_id=message_id)
        if live_post_index is None:
            raise KeyError
        return self.get_live_post_by_index(live_post_index)

    def add_live_post(self, live_post: LivePostBlock) -> None:
        """Adds a new live post to live page.

        Args:
            live_post (LivePostBlock):
                live post to add
        """

        posts = self.live_posts
        lp_index = len(posts)
        post_created_at = live_post["created"]

        while lp_index > 0:
            if posts[lp_index - 1].value["created"] < post_created_at:
                break

            lp_index -= 1

        # Insert to keep posts sorted by time
        self.live_posts.insert(lp_index, ("live_post", live_post))

        self.save_revision().publish()

    def delete_live_post(self, message_id: str) -> None:
        """Deletes the live post corresponding to message_id.

        Args:
            message_id (str):
                ID of the message corresponding to a live post.
        Raises:
            (KeyError) if live post containing message with message_id doesn't exist.
        """

        live_post_index = self.get_live_post_index(message_id=message_id)
        if live_post_index is None:
            raise KeyError
        del self.live_posts[live_post_index]

        self.save_revision().publish()

    def update_live_post(self, live_post: LivePostBlock) -> None:
        """Updates a live post when it has been edited.
        Args:
            live_post (livePostBlock): Live post to update.
        """

        live_post.value["modified"] = now()
        self.save_revision().publish()

    class Meta:
        abstract = True
