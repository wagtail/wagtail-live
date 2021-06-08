""" Block types and block constructors are defined in this module."""

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
    """A block that represents a live post content."""

    message = TextBlock(help_text="Text of the message")
    image = ImageChooserBlock(help_text="Image of the message")
    embed = EmbedBlock(help_text="URL of the embed message")


class LivePostBlock(StructBlock):
    """A generic block that maps to a message in a messaging app."""

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
    """Helper function to construct a text block for a LivePostBlock content.

    Args:
        text (str): Text to add

    Returns:
        a TextBlock
    """

    text_block = TextBlock()
    return text_block.to_python(text)


def construct_image_block(image):
    """Helper function to construct an image block for a LivePostBlock content.

    Args:
        image (pk): Foreign key to the image to add

    Returns:
        an ImageBlock
    """

    image_block = ImageChooserBlock()
    return image_block.to_python(image.id)


def construct_live_post_block(message_id, created):
    """Helper function to construct a LivePostBlock .

    Args:
        message_id (str):
            Id of the message to construct a live post for.
        created (DateTime):
            Date and time of message creation.

    Returns:
        a LivePostBlock
    """

    live_post = LivePostBlock()
    return live_post.to_python(
        {
            "message_id": message_id,
            "created": created,
        }
    )
