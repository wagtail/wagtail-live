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
