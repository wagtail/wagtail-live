from wagtail.embeds.blocks import EmbedValue
from wagtail.core.blocks import StreamValue, StructValue
from datetime import datetime
from wagtail_live.blocks import (
    ContentBlock,
    LivePostBlock,
    add_block_to_live_post,
    clear_live_post_content,
    construct_embed_block,
    construct_image_block,
    construct_text_block,
    construct_live_post_block,
)
from wagtail_live.receivers import TEXT

def test_construct_text_block():
    text_block = construct_text_block(text="Some text")
    assert text_block == "Some text"

def test_construct_embed_block():
    valid_embed = "https://www.youtube.com/watch?v=Wrc_gofwDR8"
    embed_block = construct_embed_block(url=valid_embed)

    assert isinstance(embed_block, EmbedValue)
    assert embed_block.url == valid_embed

def test_construct_live_post_block():
    live_post_block = construct_live_post_block(
        message_id="1234",
        created=datetime(1970, 1, 1, 12, 00),
    )
    assert live_post_block == StructValue(
        LivePostBlock(),
        {
            "message_id": "1234",
            "created": datetime(1970, 1, 1, 12, 00),
            "modified": None,
            "show": True,
            "content": StreamValue(ContentBlock(), []),
        },
    )

def test_add_block_to_live_post():
    text_block = construct_text_block(text="Some text")
    live_post_block = construct_live_post_block(
        message_id="1234",
        created=datetime(1970, 1, 1, 12, 00),
    )
    add_block_to_live_post(TEXT, text_block, live_post_block)

    assert live_post_block["content"] == StreamValue(
        ContentBlock(), [("text", "Some text")]
    )