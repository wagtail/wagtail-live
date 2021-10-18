""" Wagtail Live models."""

from django.conf import settings
from django.db import models
from django.utils import timezone
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField

from wagtail_live.blocks import LivePostBlock, compare_live_posts_values
from wagtail_live.signals import live_page_update


class LivePageMixin(models.Model):
    """
    Base class for pages using Wagtail Live.

    Attributes:
        channel_id (str):
            Id of the corresponding channel in a messaging app.
        last_updated_at (DateTime):
            Date and time of the last update of this page.
        live_posts (StreamField):
            StreamField containing all the posts/messages published
            respectively on this page/channel.
    """

    channel_id = models.CharField(
        help_text="Channel ID",
        max_length=255,
        blank=True,
        unique=True,
    )
    last_updated_at = models.DateTimeField(
        help_text="Last update of this page",
        blank=True,
        default=timezone.now,
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

    @property
    def last_update_timestamp(self):
        """Timestamp of the last update of this page."""

        return self.last_updated_at.timestamp()

    def save(self, sync=True, *args, **kwargs):
        """Update live page on save depending on the `WAGTAIL_LIVE_SYNC_WITH_ADMIN` setting."""

        sync_changes = sync and getattr(settings, "WAGTAIL_LIVE_SYNC_WITH_ADMIN", True)
        has_changed = False
        if sync_changes and self.id:
            renders, seen = [], set()
            previous_posts = {
                live_post.id: live_post
                for live_post in self.__class__.objects.get(id=self.id).live_posts
            }
            now = timezone.now()

            for i, post in enumerate(self.live_posts):  # New posts
                post_id = post.id
                if post_id in previous_posts:
                    seen.add(post_id)

                    # Check if the post has been modified.
                    previous_post = previous_posts[post_id]
                    identic = compare_live_posts_values(post.value, previous_post.value)
                    if not identic:
                        post.value["modified"] = now
                        renders.append(i)

                else:
                    # This is a new post.
                    # Force the value of `created` here to keep it synchronized with the
                    # `last_updated_at` property.
                    # This is mostly to avoid missing new updates with the polling publishers.
                    post.value["created"] = now
                    renders.append(i)

            removals = list(set(previous_posts.keys()).difference(seen))

            has_changed = bool(renders or removals)
            if has_changed:
                self.last_updated_at = now

        result = super().save(*args, **kwargs)

        if sync_changes and has_changed:
            # Reverse renders so the latest posts, which are in the start of the list,
            # are processed later in the front end.
            renders.reverse()
            renders = list(map(self.get_live_post_by_index, renders))

            # Send signal.
            live_page_update.send(
                sender=self.__class__,
                channel_id=self.channel_id,
                renders=renders,
                removals=removals,
            )

        return result

    def _get_live_post_index(self, message_id):
        for i, post in enumerate(self.live_posts):
            if post.value["message_id"] == message_id:
                return i

    def get_live_post_index(self, message_id):
        """
        Retrieves the index of a live post.

        Args:
            message_id (str): ID of the message corresponding to a live post.

        Returns:
            int: Index of the live post if found else -1
        """

        return self._get_live_post_index(message_id=message_id)

    def get_live_post_by_index(self, live_post_index):
        """
        Retrieves a live post by its index.

        Args:
            live_post_index (int): Index of the live post to look for.

        Returns:
            LivePostBlock: The live post instance

        Raises:
            IndexError: if a live post with the given index doesn't exist.
        """

        return self.live_posts[live_post_index]

    def get_live_post_by_message_id(self, message_id):
        """
        Retrieves a live post by its ID.

        Args:
            message_id (str):
                ID of the message corresponding to a live post.

        Returns:
            LivePostBlock: The live post instance

        Raises:
            KeyError: if a live post with the given ID doesn't exist.
        """

        live_post_index = self.get_live_post_index(message_id=message_id)
        if live_post_index is None:
            raise KeyError
        return self.get_live_post_by_index(live_post_index)

    def add_live_post(self, live_post):
        """
        Adds a new live post to live page.

        Args:
            live_post (LivePostBlock):
                live post to add
        """

        posts = self.live_posts
        lp_index = 0
        post_created_at = live_post["created"]
        while lp_index < len(posts):
            if posts[lp_index].value["created"] < post_created_at:
                break
            lp_index += 1

        # Insert to keep posts sorted by time
        self.live_posts.insert(lp_index, ("live_post", live_post))

        self.last_updated_at = post_created_at
        self.save(sync=False)

        live_post = self.get_live_post_by_index(lp_index)
        live_page_update.send(
            sender=self.__class__,
            channel_id=self.channel_id,
            renders=[live_post],
            removals=[],
        )

    def update_live_post(self, live_post):
        """
        Updates a live post when it has been edited.

        Args:
            live_post (livePostBlock):
                Live post to update.
        """

        live_post.value["modified"] = self.last_updated_at = timezone.now()
        self.save(sync=False)

        live_page_update.send(
            sender=self.__class__,
            channel_id=self.channel_id,
            renders=[live_post],
            removals=[],
        )

    def delete_live_post(self, message_id):
        """
        Deletes the live post corresponding to message_id.

        Args:
            message_id (str):
                ID of the message corresponding to a live post.
        Raises:
            KeyError: if live post containing message with message_id doesn't exist.
        """

        live_post_index = self.get_live_post_index(message_id=message_id)
        if live_post_index is None:
            raise KeyError

        live_post_id = self.live_posts[live_post_index].id
        del self.live_posts[live_post_index]

        self.last_updated_at = timezone.now()
        self.save(sync=False)

        live_page_update.send(
            sender=self.__class__,
            channel_id=self.channel_id,
            renders={},
            removals=[live_post_id],
        )

    def get_updates_since(self, last_update_ts):
        """
        Retrieves new updates since a given timestamp value.

        Args:
            last_update_ts (DateTime):
                Timestamp of the last update.

        Returns:
            (list, dict):
                a tuple containing the current live posts
                and the updated posts since `last_update_ts`.
        """

        # Reverse posts list so that latest updates are processed later by the client side.
        posts = reversed(self.live_posts)
        current_posts, updated_posts = [], {}
        for post in posts:
            post_id = post.id
            current_posts.append(post_id)

            created = post.value["created"]
            if created >= last_update_ts:  # This is a new post
                updated_posts[post_id] = {
                    "show": post.value["show"],
                    "content": post.render(context={"block_id": post.id}),
                }
                continue

            last_modified = post.value["modified"]
            if last_modified and last_modified >= last_update_ts:
                # This is an edited post
                updated_posts[post_id] = {
                    "show": post.value["show"],
                    "content": post.render(context={"block_id": post.id}),
                }

        return (updated_posts, current_posts)

    class Meta:
        abstract = True
