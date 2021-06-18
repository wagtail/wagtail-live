"""Wagtail Live receiver classes."""

import json
from abc import ABC, abstractmethod
from functools import cached_property

import requests
from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from wagtail.images import get_image_model

from .blocks import (
    construct_embed_block,
    construct_image_block,
    construct_live_post_block,
    construct_text_block,
)
from .exceptions import RequestVerificationError, WebhookSetupError
from .utils import is_embed

TEXT = "message"
IMAGE = "image"
EMBED = "embed"
LivePost = "live_post"


class BaseMessageReceiver:
    """Base Receiver class."""

    @cached_property
    def model(self):
        """
        LivePageMixin is an abstract class, so we can't make queries directly
        We have to get the actual model which subclasses it to perform queries.
        """

        app_name = getattr(settings, "LIVE_APP", "")
        model_name = getattr(settings, "LIVE_PAGE_MODEL", "")
        return apps.get_model(app_name, model_name)

    def dispatch_event(self, event):
        """Dispatches an event to find corresponding handler.

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


@method_decorator(csrf_exempt, name="dispatch")
class WebhookReceiverMixin(ABC, View):
    """Mixin for receivers using the webhook technique.

    Attributes:
        url_path (str):
            Path of the URL used by a messaging app to send new updates to this receiver.
        url_name (str):
            Name of the URL for reversing/resolving.
    """

    url_path = ""
    url_name = ""

    def pre_check_request(self, request, body, *args, **kwargs):
        """This method allows doing work outside of the receiving/publishing cycle.
        It's used for challenge verification with SLack API for example.
        """

        pass

    @abstractmethod
    def verify_request(self, request):
        """Ensures that the incoming request comes from the messaging app expected.

        Raises:
            (RequestVerificationError) if the request verification failed
        """

        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        """This is the main method for Webhook receivers.
        It handles new updates from messaging apps in these 4 steps:

        1- Call the pre_check_request hook.
        2- Verify the request.
        3- Process the updates received.
        4- Acknowledge the request.

        Args:
            request (HttpRequest): Http request

        Returns:
            (HttpResponseForbidden) if the request couldn't be verified.
            (HttpResponse) OK if the request is verified and updates have been processed
            succesfully.
        """

        body = request.body.decode("utf-8")
        payload = json.loads(body)

        pre_check_result = self.pre_check_request(request, body, payload)
        if pre_check_result:
            return pre_check_result

        try:
            self.verify_request(request, body, payload)
        except RequestVerificationError:
            return HttpResponseForbidden("Request verification failed.")

        self.dispatch_event(event=payload)
        return HttpResponse("OK")

    @classmethod
    @abstractmethod
    def webhook_connection_set(cls):
        """Checks if webhook connection is set.
        We call this method before calling the set_webhook method in order to avoid sending
        unneccesary requests to the messaging app server.

        Returns:
            (bool) True if webhook connection is set else False
        """

        raise NotImplementedError

    @classmethod
    @abstractmethod
    def set_webhook(cls):
        """Sets a webhook connection with the messaging app chosen.
        This method may be trivial for messaging apps which propose
        setting a webhook in their UI like SLack.

        Raises:
            (WebhookSetupError) if the webhook connection with the messaging app
            chosen failed.
        """

        raise NotImplementedError

    @classmethod
    def get_urls(cls):
        """Retrieves webhook urls after having ensured that a webhook connection
        is enabled with the corresponding messaging app.

        Returns:
            (URLPattern) corresponding to the URL which messaging apps use
            to send new updates.

        Raises:
            (WebhookSetupError): if the webhook connection with the messaging app
            didn't succeed.
        """

        if not cls.webhook_connection_set():
            try:
                cls.set_webhook()
            except WebhookSetupError:
                raise

        return [
            path(cls.url_path, cls.as_view(), name=cls.url_name),
        ]
