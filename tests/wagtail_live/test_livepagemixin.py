"""Wagtail Live LivePageMixin test suite."""

from datetime import timedelta

import pytest

from wagtail_live.blocks import construct_live_post_block
from wagtail_live.models import LivePageMixin
from wagtail_live.receivers import LivePost


def test_simple_live_page_instance(simple_live_page):
    """Subclasses LivePageMixin."""

    assert isinstance(simple_live_page, LivePageMixin)


def test_simple_live_page_posts_count(simple_live_page):
    """Test fixture contains 5 live posts."""

    assert len(simple_live_page.live_posts) == 5


def test_add_live_post_to_live_page(simple_live_page, live_post_block):
    """Live post is added to live page with correct data."""

    simple_live_page.add_live_post(live_post_block, live_post_block["message_id"])
    assert len(simple_live_page.live_posts) == 6

    live_post = simple_live_page.live_posts[0]
    assert live_post.id == live_post_block["message_id"]
    assert live_post.block_type == LivePost
    assert live_post.value == live_post_block


def test_add_live_post_sorts(simple_live_page):
    """Live posts are inserted by creation date-time."""

    third_post = simple_live_page.get_live_post_by_index(live_post_index=2)
    third_post_created_at = third_post.value["created"]
    new_live_post = construct_live_post_block(
        message_id="123",
        created=third_post_created_at - timedelta(minutes=1),
    )
    simple_live_page.add_live_post(new_live_post, new_live_post["message_id"])

    assert simple_live_page.get_live_post_index(live_post_id="123") == 2
    assert simple_live_page.get_live_post_index(live_post_id="3") == 3


def test_get_live_post_index(simple_live_page):
    """Returns the correct index if the live post exists else -1."""

    live_post_index = simple_live_page.get_live_post_index(live_post_id="3")
    assert live_post_index == 2

    live_post_index = simple_live_page.get_live_post_index(live_post_id="1")
    assert live_post_index == 0

    live_post_index = simple_live_page.get_live_post_index(live_post_id="5")
    assert live_post_index == 4

    live_post_index = simple_live_page.get_live_post_index(live_post_id="0")
    assert live_post_index == -1


def test_get_live_post_by_index(simple_live_page, live_post_block):
    """Returns the correct live post if the index given is valid."""

    simple_live_page.add_live_post(live_post_block, live_post_block["message_id"])

    # live_post_block is supposed to be created in 1970,
    # therefore it's inserted at the start of the list.
    live_post = simple_live_page.get_live_post_by_index(live_post_index=0)
    assert live_post.value == live_post_block


def test_get_live_post_by_index_error(simple_live_page):
    """Raises IndexError if the index given is invalid."""

    with pytest.raises(IndexError):
        simple_live_page.get_live_post_by_index(live_post_index=5)


def test_get_live_page_by_id(simple_live_page, live_post_block):
    """Returns the correct live post if the id given is valid."""

    simple_live_page.add_live_post(live_post_block, live_post_block["message_id"])
    live_post = simple_live_page.get_live_post_by_id(
        live_post_id=live_post_block["message_id"]
    )

    assert live_post.value == live_post_block


def test_get_live_page_by_id_error(simple_live_page, live_post_block):
    """Raises KeyError if the id given is invalid."""

    with pytest.raises(KeyError):
        # live_post_block isn't added so it shouldn't be found.
        simple_live_page.get_live_post_by_id(live_post_block["message_id"])


def test_delete_live_post(simple_live_page):
    """Deletes a live post if the id is valid."""

    simple_live_page.delete_live_post(live_post_id="2")
    assert len(simple_live_page.live_posts) == 4
    with pytest.raises(KeyError):
        simple_live_page.get_live_post_by_id(live_post_id="2")


def test_delete_live_post_with_invalid_id(simple_live_page, live_post_block):
    """Raises KeyError if the id given is invalid."""

    with pytest.raises(KeyError):
        simple_live_page.delete_live_post(live_post_id=live_post_block["message_id"])

    # live_posts hasn't changed
    assert len(simple_live_page.live_posts) == 5


def test_update_live_post(simple_live_page, live_post_block):
    """LivePageMixin last_update_at field is synced with live posts updates."""

    last_post = simple_live_page.get_live_post_by_index(live_post_index=4)
    simple_live_page.update_live_post(last_post)

    diff = simple_live_page.last_update_at - last_post.value["modified"]
    assert diff.total_seconds() == pytest.approx(0.0, abs=1e-5)
