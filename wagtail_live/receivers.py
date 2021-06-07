"""Wagtail Live receiver classes."""

import re

import requests
from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.utils.timezone import now
from wagtail.embeds.oembed_providers import all_providers
from wagtail.images import get_image_model

from .blocks import (
    construct_embed_block,
    construct_image_block,
    construct_live_post_block,
    construct_text_block,
)

TEXT = "message"
IMAGE = "image"
EMBED = "embed"
LivePost = "live_post"


def is_embed(text):
    """Checks if a text is a link to embed.

    Args:
        text (str): Text to check

    Returns:
        (bool) True if text corresponds to an embed link False else
    """

    for provider in all_providers:
        for url_pattern in provider.get("urls", []):
            # Somehow Slack links start with `<` and end with `>`.
            if bool(re.match(url_pattern, text)):
                return True

    return False


class BaseMessageReceiver:
    """Base Receiver class."""

    def __init__(self, app_name, model_name):
        """
        LivePageMixin is an abstract class, so we can't make queries directly
        We have to get the actual page which subclasses it to perform queries.
        """

        self.model = apps.get_model(app_name, model_name)

    def dispatch(self, event):
        """Dispatch an event to find corresponding handler.

        Args:
            event: New event from a messaging app.
        """

        raise NotImplementedError

    def get_channel_id_from_message(self, message):
        """Retrieves a channel ID from a message.

        Args:
            message: A received message from a messaging app

        Returns:
            ID of the channel which the given message belongs to
        """

        raise NotImplementedError

    def get_live_page_from_channel_id(self, channel_id):
        """Retrieves the live page with a given channel ID.

        Args:
            channel_id (str): Channel ID

        Returns:
            (LivePageMixin) The livepage corresponding to channel ID.

        Raises:
            Http404 if a page with the given channel ID doesn't exist.
        """

        return get_object_or_404(self.model, channel_id=channel_id)

    def get_message_id_from_message(self, message):
        """Retrieves message's ID.

        Args:
            message: A received message from a messaging app

        Returns:
            Id of the given message
        """

        raise NotImplementedError

    def get_message_text(self, message):
        """Retrieves the text of a message.

        A message is made of text and files.

        Args:
            message: A received message from a messaging app

        Returns:
            (str) Text of the given message.
        """

        raise NotImplementedError

    def get_message_files(self, message):
        """Retrieves the files of a message.

        A message is made of text and files.

        Args:
            message: A received message from a messaging app

        Returns:
            (list) of files included in the given message.
        """

        raise NotImplementedError

    def get_message_id_from_edited_message(self, message):
        """Retrieves the ID of the original message.

        Args:
            message: A received message from a messaging app

        Returns:
            ID of the original message thet is being edited.
        """

        raise NotImplementedError

    def get_message_text_from_edited_message(self, message):
        """Retrieves the text an edited message

        Args:
            message: A received message from a messaging app

        Returns:
            Text of the edited message
        """

        raise NotImplementedError

    def get_message_files_from_edited_message(self, message):
        """Retrieves the files  from an edited message

        Args:
            message: A received message from a messaging app

        Returns:
            files of the edited message
        """

        raise NotImplementedError

    def get_embed(self, text):
        """Check if a text is an embed for this receiver and return embed URL if so.
        
        Args:
            text (str): Text to check

        Returns:
            (str) URL of the embed if the text contains an embed, else "".
        """

        return text if is_embed(text=text) else ""

    def process_text(self, live_page, live_post, message_text):
        """Processes the text of a message.

        Parses the message, constructs corresponding block types
        i.e Embed or Text and add those blocks to the given
        live post.

        Args:
            live_page (LivePageMixin):
                Live page to update
            live_post (LivePostBlock):
                Live post to update
            message_text (str):
                Text to add to a live post.
        """

        message_parts = message_text.split("\n")
        for text in message_parts:
            block_type = ""

            url = self.get_embed(text=text)
            if url:
                block = construct_embed_block(url=url)
                block_type = EMBED

            else:
                block = construct_text_block(text=text)
                block_type = TEXT

            live_page.add_block_to_live_post(
                block_type=block_type,
                block=block,
                live_block=live_post,
            )

    def process_files(self, live_page, live_post, files):
        """Processes the files of a message.

        Creates the corresponding block for any file and add it
        to the given live post.

        Args:
            live_page (LivePageMixin):
                Live page to update
            live_post (LivePostBlock):
                Live post to update
            files (list):
                Files to add to a live post.
        """

        for item in files:
            mime_type = item["mimetype"]
            if mime_type in ["image/png", "image/jpeg", "image/gif"]:

                filename = item.get("name")
                file_url = item["url_private"]
                headers = {"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"}
                response = requests.get(file_url, headers=headers)

                img = get_image_model()(
                    title=slugify(filename).replace("-", " "),
                    file=ContentFile(
                        response.content,
                        name=filename,
                    ),
                )
                img.save()
                block = construct_image_block(image=img)
                live_page.add_block_to_live_post(
                    block_type=IMAGE,
                    block=block,
                    live_block=live_post,
                )

    def add_message(self, message):
        """Adds a received message from a messaging app to the corresponding channel.

        Args:
            message: A message received from a messaging app
        """

        message_id = self.get_message_id_from_message(message=message)
        channel_id = self.get_channel_id_from_message(message=message)
        try:
            live_page = self.get_live_page_from_channel_id(channel_id=channel_id)
        except Http404:
            # maybe create the LivePage here?
            return

        live_post = construct_live_post_block(message_id=message_id, created=now())

        message_text = self.get_message_text(message=message)
        self.process_text(
            live_page=live_page, live_post=live_post, message_text=message_text
        )

        files = self.get_message_files(message=message)
        self.process_files(live_page=live_page, live_post=live_post, files=files)

        live_page.add_live_post(live_post=live_post, live_post_id=message_id)

    def change_message(self, message):
        """Changes a message when it's edited from a messaging app.

        Args:
            message: A message edited from a messaging app
        """

        message_id = self.get_message_id_from_edited_message(message=message)
        channel_id = self.get_channel_id_from_message(message=message)
        try:
            live_page = self.get_live_page_from_channel_id(channel_id=channel_id)
        except Http404:
            return

        live_post = live_page.get_live_post_by_id(live_post_id=message_id)
        live_page.clear_live_post_content(live_post=live_post)

        message_text = self.get_message_text_from_edited_message(message=message)
        self.process_text(
            live_page=live_page, live_post=live_post.value, message_text=message_text
        )

        files = self.get_message_files_from_edited_message(message=message)
        self.process_files(live_page=live_page, live_post=live_post.value, files=files)

        live_page.update_live_post(live_post=live_post)

    def delete_message(self, message):
        """Deletes a message when it's deleted from a messaging app.

        Args:
            message: A message deleted from a messaging app
        """

        message_id = self.get_message_id_from_edited_message(message=message)
        channel_id = self.get_channel_id_from_message(message=message)
        try:
            live_page = self.get_live_page_from_channel_id(channel_id=channel_id)
        except Http404:
            return

        live_page.delete_live_post(live_post_id=message_id)
