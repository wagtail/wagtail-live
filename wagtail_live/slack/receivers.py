""" How to use it?

To create an app, register your URL to slack, get a token plus all additional infrastucture, see:
https://github.com/slackapi/bolt-python/tree/main/examples/django

Then do something like this in your url_patterns:

from wagtail_live.slack.views import slack_events_handler

url_patterns += [
    path("slack/events", slack_events_handler, name="slack_events_handler"),
]

Add the following to your settings.py file:

LIVE_PAGE_MODEL = "model name"
LIVE_APP = "app name"
SLACK_BOT_TOKEN = "your slack bot token"
SLACK_SIGNING_SECRET = "your slack signing secret"

And you are good to go! (Soon hopefully!)

"""

import re

import requests
from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils.timezone import now
from wagtail.core.blocks import TextBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.embeds.oembed_providers import all_providers
from wagtail.images import get_image_model
from wagtail.images.blocks import ImageChooserBlock

from ..blocks import ContentBlock, LivePostBlock

TEXT = "message"
IMAGE = "image"
EMBED = "embed"
LivePost = "live_post"


def construct_text_block(text):
    text_block = TextBlock()
    return text_block.to_python(text)


def construct_image_block(image):
    image_block = ImageChooserBlock()
    return image_block.to_python(image.id)


def construct_embed_block(url):
    embed_block = EmbedBlock()
    return embed_block.to_python(url)


def construct_live_post_block(message_id):
    live_post = LivePostBlock()
    return live_post.to_python(
        {
            "message_id": message_id,
            "created": now(),
        }
    )


def add_block_to_live_post_block(block_type, block, live_block):
    live_block["content"].append((block_type, block))


def is_embed(text):
    for provider in all_providers:
        for url_pattern in provider.get("urls", []):
            # Somehow Slack links start with `<` and end with `>`.
            if bool(re.match(url_pattern, text)):
                return True

    return False


class SlackEventsAPIReceiver:
    def __init__(self, app_name, model_name):
        # LivePageMixin is an abstract class, so we can't make queries directly
        # We have to get the actual page which subclasses it to perform queries
        self.model = apps.get_model(app_name, model_name)

    def dispatch(self, message):
        if "subtype" in message and message["subtype"] == "message_changed":
            self.change_message(message)
            return

        elif "subtype" in message and message["subtype"] == "message_deleted":
            self.delete_message(message)
            return

        else:
            self.add_message(message)

    def get_channel_name_from_message(self, message):
        return message["channel"]

    def get_live_page_from_channel_name(self, channel_name):
        return self.model.objects.get(channel_name=channel_name)

    def get_message_id_from_message(self, message):
        return message["ts"]

    def get_message_text(self, message):
        return message["text"]

    def get_message_files(self, message):
        if "files" in message:
            return message["files"]
        return []

    def get_message_id_from_edited_message(self, message):
        return self.get_message_id_from_message(message["previous_message"])

    def get_message_text_from_edited_message(self, message):
        return self.get_message_text(message["message"])

    def get_message_files_from_edited_message(self, message):
        return self.get_message_files(message["message"])

    def process_text(self, live_post, message_text):
        message_parts = message_text.split("\n")
        for part in message_parts:
            block_type = ""

            if is_embed(part[1:-1]):
                # Strip leading `<` and trailing `>`.
                # Not sure if it's the normal behavior, but have repeatedly received links
                # from SLack API that looks like below:
                # <https://twitter.com/lephoceen/status/139?s=20|https://twitter.com/lephoceen/status/139?s=20>'

                url = part[1:-1].split("|")[0]
                block = construct_embed_block(url)
                block_type = EMBED

            else:
                block = construct_text_block(part)
                block_type = TEXT

            add_block_to_live_post_block(block_type, block, live_post)

    def process_files(self, live_post, files):
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
                block = construct_image_block(img)
                add_block_to_live_post_block(IMAGE, block, live_post)

    def add_message(self, message):
        channel_name = self.get_channel_name_from_message(message)
        live_page = self.get_live_page_from_channel_name(channel_name)
        message_id = self.get_message_id_from_message(message)

        live_post = construct_live_post_block(message_id)

        message_text = self.get_message_text(message)
        self.process_text(live_post, message_text)

        files = self.get_message_files(message)
        self.process_files(live_post, files)

        # Finally, add live post to live page and save it.
        # live_post is also saved with ID equals to message's ID;
        # this facilitates tracking blocks
        live_page.live_posts.append(("live_post", live_post, message_id))
        live_page.last_update_at = now()
        live_page.save()

    def delete_message(self, message):
        channel_name = self.get_channel_name_from_message(message)
        live_page = self.get_live_page_from_channel_name(channel_name)
        message_id = self.get_message_id_from_edited_message(message)

        live_post_index = live_page.get_live_post_index(live_post_id=message_id)
        del live_page.live_posts[live_post_index]
        live_page.last_update_at = now()
        live_page.save()

    def change_message(self, message):
        channel_name = self.get_channel_name_from_message(message)
        live_page = self.get_live_page_from_channel_name(channel_name)
        message_id = self.get_message_id_from_edited_message(message)

        live_post_index = live_page.get_live_post_index(live_post_id=message_id)
        live_post = live_page.get_live_post(live_post_index=live_post_index)
        live_post.value.get("content").clear()

        message_text = self.get_message_text_from_edited_message(message)
        self.process_text(live_post.value, message_text)

        files = self.get_message_files_from_edited_message(message)
        self.process_files(live_post.value, files)

        live_post.value["modified"] = now()
        live_page.last_update_at = now()
        live_page.save()
