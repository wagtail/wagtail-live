""" Block types and block constructors are defined in this module."""

from wagtail.admin.rich_text.converters.editor_html import EditorHTMLConverter
from wagtail.core import rich_text
from wagtail.core.blocks import (
    BooleanBlock,
    CharBlock,
    DateTimeBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    StructValue,
)
from wagtail.embeds.blocks import EmbedBlock, EmbedValue
from wagtail.images.blocks import ImageChooserBlock


class ContentBlock(StreamBlock):
    """A block that represents a live post content."""

    text = RichTextBlock(help_text="Text of the message")
    image = ImageChooserBlock(help_text="Image of the message")
    embed = EmbedBlock(help_text="URL of the embed message")


class LivePostBlock(StructBlock):
    """A generic block that maps to a message in a messaging app."""

    message_id = CharBlock(help_text="Message's ID")
    created = DateTimeBlock(
        required=False, help_text="Date and time of message creation"
    )
    modified = DateTimeBlock(
        required=False,
        help_text="Date and time of last update",
    )
    show = BooleanBlock(
        required=False,
        help_text="Indicates if this message is shown/hidden",
        default=True,
    )
    content = ContentBlock()

    class Meta:
        template = "wagtail_live/blocks/live_post.html"


def construct_text_block(text):
    """
    Helper function to construct a text block for a LivePostBlock content.

    Args:
        text (str): Text to add

    Returns:
        RichText: a TextBlock filled with the given text.
    """

    # Make sure no malicious html is accepted
    # BeautifulSoup prefers markup that contains at least 1 tag,
    # if that's not the case we can accept the input as is.
    if "<" in text:
        features = rich_text.features.get_default_features()
        cleaned_text = EditorHTMLConverter(features=features).whitelister.clean(text)
    else:
        cleaned_text = text

    return RichTextBlock().to_python(cleaned_text)


def construct_image_block(image):
    """
    Helper function to construct an image block for a LivePostBlock content.

    Args:
        image (pk): Foreign key to the image to add

    Returns:
        ImageBlock: an ImageBlock filled with the given image.
    """

    return ImageChooserBlock().to_python(image.id)


def construct_embed_block(url):
    """
    Helper function to construct an embed block for a LivePostBlock content.

    Args:
        url (str): Url of the embed

    Returns:
        EmbedBlock: an EmbedBlock filled with the given url.
    """

    return EmbedBlock().to_python(url)


def construct_live_post_block(message_id, created):
    """
    Helper function to construct a LivePostBlock.

    Args:
        message_id (str):
            Id of the message to construct a live post for.
        created (DateTime):
            Date and time of message creation.

    Returns:
        LivePostBlock: a LivePostBlock
    """

    return LivePostBlock().to_python(
        {
            "message_id": message_id,
            "created": created,
        }
    )


def add_block_to_live_post(block_type, block, live_block):
    """
    Adds a new content block to a live post.

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


def clear_live_post_content(live_post):
    """
    Clears the content of a live post.

    Args:
        live_post (livePostBlock): Live post which content will be cleared.
    """

    if isinstance(live_post, StructValue):
        live_post["content"].clear()
    else:
        live_post.value["content"].clear()


def compare_live_posts_values(first_post_value, second_post_value):
    """
    Compares the values of two live posts.

    Args:
        first_post_value (StreamValue):   First live post.
        second_post_value (StreamValue):  Second live post.

    Returns:
        bool: True if the live posts are identic, False else.
    """

    if first_post_value["show"] != second_post_value["show"]:
        return False

    first_content = first_post_value["content"]
    second_content = second_post_value["content"]
    if len(first_content) != len(second_content):
        return False

    for i in range(0, len(first_content)):
        first_item = first_content[i]
        second_item = second_content[i]
        if (
            first_item.block_type != second_item.block_type
            or first_item.id != second_item.id
        ):
            return False

        first_value = first_item.value
        second_value = second_item.value
        if isinstance(first_value, rich_text.RichText):
            first_value = rich_text.get_text_for_indexing(first_value.source)
            second_value = rich_text.get_text_for_indexing(second_value.source)
        elif isinstance(first_value, EmbedValue):
            first_value = first_value.url
            second_value = second_value.url

        if first_value != second_value:
            return False

    return True
