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
        """ Retrieve index of a live post in page's live posts.

        Uses binary search since live posts are sorted by timestamp.
        This implementation may change.

        Args:
            live_post_id (str):
                ID of the live post to look for.
            low (int):
                Index of first element in page live posts.
            high (int):
                Index of last element in page live_posts.

        Returns:
            (int) Index of the live post if found else -1
        """
        
        while low < high:
            mid = (low + high) // 2
            curr_id = self.live_posts[mid].id

            if float(curr_id) == float(live_post_id):
                return mid

            elif float(curr_id) < float(live_post_id):
                low = mid + 1

            else:
                high = mid - 1
        
        if self.live_posts[low].id != live_post_id:
            return -1
        return low

    def get_live_post_index(self, live_post_id):
        """Retrieve index of a livepost with its ID.
        
        Args:
            live_post_id (str); Id of the live post to look for.

        Returns:
            (int) Index of the live post if found else -1
        """

        return self._get_live_post_index(live_post_id, 0, len(self.live_posts))

    def get_live_post_by_index(self, live_post_index):
        """Retrieve a live post by its index.
        
        Args: 
            live_post_index (str): Index of the live post to look for.

        Returns:
            (LivePostBlock) The live post instance

        Raises:
            (someException) if a live post with the given index doesn't exist.
        """

        try:
            live_post = self.live_posts[live_post_index]
        except KeyError:
            raise 
        return live_post

    def get_live_post_by_id(self, live_post_id):
        """Retrieve a live post by its ID.
        
        Args: 
            live_post_id (str): ID of the live post to look for.

        Returns:
            (LivePostBlock) The live post instance

        Raises:
            (someException) if a live post with the given ID doesn't exist.
        """

        live_post_index = self.get_live_post_index(live_post_id=live_post_id)
        if live_post_index == -1:
            raise
        return self.get_live_post_by_index(live_post_index)

    def add_block_to_live_post(self, block_type, block, live_block):
        """ Add a new content block to a live post.
        
        Args:
            block_type (str):
                Type of the block to add
            block (Block):
                Block to add to the live post.
            live_block (LivePostBlock):
                Live post in which the new block will be added.
        """

        live_block["content"].append((block_type, block))

    def add_live_post(self, live_post, live_post_id):
        """ Add a new live post to live page.

        Live posts are added with a custom ID to facilitate
        keeping their track. 
        By default, the value of a live post's ID is
        the timestamp of the corresponding message creation. 
        A check is also done to ensure that live posts are always
        sorted by time.

        Args:
            live_post (LivePostBlock):
                live post to add
            live_post_id (str):
                Id of the new live_post
        """

        lp_index = len(self.live_posts) if self.live_posts else 0
        post_id = float(live_post_id)
        while self.live_posts and float(self.live_posts[lp_index - 1].id) > post_id:
            lp_index -= 1

        # Insert to keep posts sorted by time
        self.live_posts.insert(lp_index, ("live_post", live_post, live_post_id))

        self.last_update_at = now()
        self.save()

    def delete_live_post(self, live_post_id):
        """Delete a live post by its ID.
        
        Args:
            live_post_id (str): Id of the live post to delete.

        Raises:
            (someException) if live post with the given ID doesn't exist.
        """

        live_post_index = self.get_live_post_index(live_post_id=live_post_id)
        if live_post_index == -1:
            raise
        del self.live_posts[live_post_index]
        self.last_update_at = now()
        self.save()

    def clear_live_post_content(self, live_post):
        """Clears the content of a live post.

        Args:
            live_post (livePostBlock): Live post which content will be cleared.
        """
    
        live_post.value.get("content").clear()

    def update_live_post(self, live_post):
        """Update a live post when it has been edited.

        Args:
            live_post (livePostBlock): Live post to update.
        """
    
        live_post.value["modified"] = now()
        self.last_update_at = now()
        self.save()

    class Meta:
        abstract = True
