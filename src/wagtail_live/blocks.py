""" Block types and block constructors are defined in this module."""
from datetime import datetime
from typing import Optional, Union

from wagtail.core.blocks import (
    Block,
    BooleanBlock,
    CharBlock,
    DateTimeBlock,
    StreamBlock,
    StreamValue,
    StructBlock,
    StructValue,
    TextBlock,
)
from wagtail.embeds.blocks import EmbedBlock, EmbedValue
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import AbstractImage


class ContentBlock(StreamBlock):
    """A block that represents a live post content."""

    text = TextBlock(help_text="Text of the message")
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
        default=True,
    )
    content = ContentBlock()


def construct_text_block(text: str) -> str:
    """Helper function to construct a text block for a LivePostBlock content.

    Args:
        text (str): Text to add

    Returns:
        a TextBlock
    """

    return TextBlock().to_python(text)


def construct_image_block(image: AbstractImage) -> AbstractImage:
    """Helper function to construct an image block for a LivePostBlock content.

    Args:
        image (pk): Foreign key to the image to add

    Returns:
        an ImageBlock
    """

    return ImageChooserBlock().to_python(image.pk)


def construct_embed_block(url: str) -> Optional[EmbedValue]:
    """Helper function to construct an embed block for a LivePostBlock content.

    Args:
        url (str): Url of the embed

    Returns:
        an EmbedBlock
    """

    return EmbedBlock().to_python(url)


def construct_live_post_block(message_id: str, created: datetime) -> StructValue:
    """Helper function to construct a LivePostBlock .

    Args:
        message_id (str):
            Id of the message to construct a live post for.
        created (DateTime):
            Date and time of message creation.

    Returns:
        a LivePostBlock
    """

    return LivePostBlock().to_python(
        {
            "message_id": message_id,
            "created": created,
        }
    )


def add_block_to_live_post(
    block_type: str, block: Block, live_block: Union[StructValue, StreamValue.StreamChild]
) -> None:
    """Adds a new content block to a live post.
    Args:
        block_type (str):
            Type of the block to add
        block (Block):
            Block to add to the live post.
        live_block (LivePostBlock):
            Live post in which the new block will be added.
    """

    if isinstance(live_block, StructValue):
        live_block["content"].append((block_type, block))
    else:
        live_block.value["content"].append((block_type, block))


def clear_live_post_content(live_post: Union[StructValue, StreamValue.StreamChild]) -> None:
    """Clears the content of a live post.
    Args:
        live_post (livePostBlock): Live post which content will be cleared.
    """

    if isinstance(live_post, StructValue):
        live_post["content"].clear()
    else:
        live_post.value["content"].clear()
