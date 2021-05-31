""" Block types are defined in this module."""

from wagtail.core.blocks import (
    BooleanBlock,
    CharBlock,
    DateTimeBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
)
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


class ContentBlock(StreamBlock):
    message = TextBlock(help_text="Text of the message")
    image = ImageChooserBlock(help_text="Image of the message")
    embed = EmbedBlock(help_text="URL of the embed message")


class LivePostBlock(StructBlock):
    """A generic block that maps to a message in a messaging app.

    Attributes:
        message_id (str):
            Represents the message's id.
        created (DateTime):
            Indicates when the message was first sent.
        modified (DateTime):
            Indicates when the message was last modified.
        show (Boolean):
            Optional; Indicates if the message is shown or not
            in the corresponding page.
    """

    message_id = CharBlock(help_text="Message's ID")
    created = DateTimeBlock(help_text="Date and time of message creation")
    modified = DateTimeBlock(
        required=False,
        help_text="Date and time of last update",
        blank=True,
    )
    show = BooleanBlock(
        required=False,
        help_text="Indicates if this message is shown/hidden",
    )
    content = ContentBlock()


def construct_text_block(text):
    text_block = TextBlock()
    return text_block.to_python(text)


def construct_image_block(image):
    image_block = ImageChooserBlock()
    return image_block.to_python(image.id)


def construct_embed_block(url):
    embed_block = EmbedBlock()
    return embed_block.to_python(url)


def construct_live_post_block(message_id, created):
    live_post = LivePostBlock()
    return live_post.to_python(
        {
            "message_id": message_id,
            "created": created,
        }
    )
