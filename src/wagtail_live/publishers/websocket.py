class BaseWebsocketPublisher:
    """Base class for publishers using the websocket technique."""

    def __call__(self, sender, channel_id, renders, removals, **kwargs):
        """Listens to the live_page_update signal.

        Args:
            sender (LivePageMixin):
                Sender of the signal
            channel_id (str):
                ID of the channel corresponding to the updated page
            renders (dict):
                Dict containing the new posts and the edited posts of the updated page
            removals (list):
                List containing the id of the deleted posts for the updated page

        Returns:
            (None)
        """

        renders = {
            post.id: post.render(context={"block_id": post.id}) for post in renders
        }
        return self.publish(channel_id=channel_id, renders=renders, removals=removals)

    def publish(self, channel_id, renders, removals):
        """Sends a new update:
        - to the "channel_id group" for django channels
        - to an event bus for separate websocket servers
        - to the websocket client for hosted websocket services

        Args:
            channel_id (str):
                ID of the channel corresponding to the updated page
            renders (dict):
                Dict containing the new posts and the edited posts of the updated page
            removals (list):
                List containing the id of the deleted posts for the updated page

        Returns:
            (None)

        Raises:
            NotImplementedError
        """

        raise NotImplementedError
