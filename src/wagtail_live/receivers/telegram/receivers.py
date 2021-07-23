import logging

import requests
from django.core.files.base import ContentFile

from wagtail_live.exceptions import RequestVerificationError, WebhookSetupError
from wagtail_live.receivers.base import BaseMessageReceiver, WebhookReceiverMixin
from wagtail_live.utils import is_embed

from .utils import (
    get_base_telegram_url,
    get_telegram_bot_token,
    get_telegram_webhook_url,
)

logger = logging.getLogger(__name__)


class TelegramWebhookMixin(WebhookReceiverMixin):
    """Telegram WebhookMixin."""

    url_path = "telegram/events/<str:token>/"
    url_name = "telegram_events_handler"

    def verify_request(self, request, body, token, *args, **kwargs):
        """See base class."""

        if token != get_telegram_bot_token():
            raise RequestVerificationError

    @classmethod
    def webhook_connection_set(cls):
        """See base class."""

        response = requests.get(get_base_telegram_url() + "getWebhookInfo")
        if response.ok:
            # Ensure that the webhook is set with the correct URL
            payload = response.json()
            return (
                payload["ok"] and payload["result"]["url"] == get_telegram_webhook_url()
            )
        return False

    @classmethod
    def set_webhook(cls):
        """Sets webhook connection with Telegram's API"""

        response = requests.get(
            get_base_telegram_url() + "setWebhook",
            params={
                "url": get_telegram_webhook_url(),
                "allowed_updates": [
                    "message",
                    "edited_message",
                    "channel_post",
                    "edited_channel_post",
                ],
            },
        )
        payload = response.json()

        if not response.ok or not payload["ok"]:
            raise WebhookSetupError(
                "Failed to set Webhook connection with Telegram's API. "
                + f"{payload['description']}"
            )


class TelegramWebhookReceiver(TelegramWebhookMixin, BaseMessageReceiver):
    """Telegram webhook receiver."""

    def dispatch_event(self, event):
        """Telegram doesn't send an update when a message is deleted.
        See base class.
        """

        for edit_type in ["edited_message", "edited_channel_post"]:
            if edit_type in event:
                self.change_message(message=event.get(edit_type))
                return

        message = event.get("message") or event.get("channel_post")
        if "media_group_id" in message:
            try:
                self.add_image_to_message(message=message)
                return
            except KeyError:
                pass

        if "entities" in message and message["entities"][0]["type"] == "bot_command":
            self.handle_bot_command(message=message)
            return

        self.add_message(message=message)

    def add_image_to_message(self, message):
        """Telegram sends images uploaded in a message one by one."""

        channel_id = self.get_channel_id_from_message(message=message)
        try:
            live_page = self.get_live_page_from_channel_id(channel_id=channel_id)
        except self.model.DoesNotExist:
            return

        message_id = self.get_message_id_from_message(message=message)
        live_post = live_page.get_live_post_by_message_id(message_id=message_id)

        files = self.get_message_files(message=message)
        self.process_files(live_post=live_post.value, files=files)

        live_page.update_live_post(live_post=live_post)

    def handle_bot_command(self, message):
        """Handles the following bot commands:
        /get_chat_id: returns the id of the current chat.
        """

        command = message["entities"][0]
        start = command["offset"]
        end = start + command["length"]
        command_text = message["text"][start:end]

        if command_text == "/get_chat_id":
            chat_id = self.get_channel_id_from_message(message=message)
            response = requests.get(
                get_base_telegram_url() + "sendMessage",
                params={
                    "chat_id": chat_id,
                    "text": chat_id,
                },
            )

            payload = response.json()
            if not payload["ok"]:
                logger.error(payload["description"])

    def get_channel_id_from_message(self, message):
        """See base class."""

        # Since live posts aren't cleaned when they are added via a receiver,
        # we make sure at this level that we return the correct types.
        return str(message["chat"]["id"])

    def get_message_id_from_message(self, message):
        """Messages containing multiple images have a media_group_id attribute.
        See base class.
        """

        msg_id = message.get("media_group_id") or message.get("message_id")
        return str(msg_id)

    def get_message_text(self, message):
        """See base class."""

        # Telegram parses the text of a message before sending it.
        # The result can be found in the message's "entities".
        return {
            "text": message.get("text") or message.get("caption") or "",
            "entities": message.get("entities", []),
        }

    def process_text(self, live_post, message_text):
        """Use the message entities to convert links.
        A raw link isn't converted by Telegram.
        A link with a description is sent as a `text_link` entity.
        See base class.
        """

        text = message_text["text"]
        len_text = len(text)
        entities = message_text["entities"]

        # Process the entities in reversed order to be able to edit the text in place.
        for entity in reversed(entities):
            url = ""
            start = entity["offset"]
            end = start + entity["length"]

            if entity["type"] == "url":
                url = description = text[start:end]

                if is_embed(url):
                    # Check if this can match an embed block, if so no conversion happens.
                    # It matches an embed block if it has a line in the text for itself.
                    if end == len_text or text[end] == "\n":
                        if start == 0 or text[start - 1] == "\n":
                            # This is an embed block, skip to the next entity
                            continue

            if entity["type"] == "text_link":
                url = entity["url"]
                description = text[start:end]

            if url:
                link = f'<a href="{url}">{description}</a>'
                text = text[:start] + link + text[end:]

        return super().process_text(live_post=live_post, message_text=text)

    def get_file_path(self, file_id):
        """Retrieves the file_path of a Telegram file.
        The file_path is necessary to have more infos about the image and download it.

        Args:
            file_id (str): Id of the file to download.

        Returns:
            (str) The file_path property of the file as sent by Telegram.
        """

        response = requests.get(
            get_base_telegram_url() + "getFile", params={"file_id": file_id}
        )
        return response.json()["result"]["file_path"]

    def get_message_files(self, message):
        """See base class."""

        if "photo" in message:
            # Choose original photo which is the last of the list
            photo = message["photo"][-1]
            photo["file_path"] = self.get_file_path(file_id=photo["file_id"])
            return [photo]
        return []

    def get_image_title(self, image):
        """See base class."""

        return image["file_path"].split("/")[-1].split(".")[0]

    def get_image_name(self, image):
        """See base class."""

        return image["file_path"].split("/")[-1]

    def get_image_mimetype(self, image):
        """See base class."""

        mimetype = image["file_path"].split("/")[-1].split(".")[-1]
        return "jpeg" if mimetype == "jpg" else mimetype

    def get_image_content(self, image):
        """See base class."""

        file_path = image["file_path"]
        response = requests.get(
            f"https://api.telegram.org/file/bot{get_telegram_bot_token()}/{file_path}"
        )
        return ContentFile(response.content)

    def get_image_dimensions(self, image):
        """See base class."""

        return image["width"], image["height"]

    def get_message_id_from_edited_message(self, message):
        """See base class."""

        return self.get_message_id_from_message(message=message)

    def get_message_text_from_edited_message(self, message):
        """See base class."""

        return self.get_message_text(message=message)

    def get_message_files_from_edited_message(self, message):
        """See base class."""

        return self.get_message_files(message=message)
