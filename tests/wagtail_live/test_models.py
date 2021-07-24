import json
from datetime import datetime

import pytest
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks.stream_block import StreamValue
from wagtail.core.models import Page

from tests.testapp.models import BlogPage
from wagtail_live.blocks import construct_live_post_block
from wagtail_live.models import LivePageMixin
from wagtail_live.signals import live_page_update


@pytest.mark.django_db
def test_live_page_mixin():
    """Global tests for LivePageMixin."""

    # LivePageMixin is an abstract model, and cannot be instantiated.
    # We use the `BlogPage` instead.
    assert isinstance(BlogPage(), (LivePageMixin, Page))
    assert hasattr(LivePageMixin, "panels")
    assert isinstance(LivePageMixin.panels[0], FieldPanel)
    assert LivePageMixin.panels[0].field_name == "channel_id"
    assert isinstance(LivePageMixin.panels[1], StreamFieldPanel)
    assert LivePageMixin.panels[1].field_name == "live_posts"
    assert LivePageMixin._meta.abstract is True


@pytest.mark.django_db
def test_live_page_mixin_channel_id_is_optional(blog_page_factory):
    """channel_id field is optional."""

    page = blog_page_factory(channel_id="", live_posts=[])
    assert page.channel_id == ""


@pytest.mark.django_db
def test_channel_field_is_unique(blog_page_factory):
    blog_page_factory(channel_id="some-id")
    expected_err = "Blog page with this Channel id already exists."

    with pytest.raises(ValidationError, match=expected_err):
        blog_page_factory(channel_id="some-id")


def test_live_page_mixin_live_posts_is_optional():
    """live_posts field is optional."""

    assert LivePageMixin.live_posts.field.blank is True


@pytest.mark.django_db
def test_last_update_timestamp(blog_page_factory):
    page = blog_page_factory(channel_id="some-id")

    assert page.last_update_timestamp == page.last_updated_at.timestamp()


@pytest.mark.django_db
def test_live_page_mixin_get_live_post_index(blog_page_factory):
    "Returns the correct index for an existing live post and None else."

    message_id_0 = "some_message_id"
    message_id_1 = "other_message_id"
    live_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "irrelevant",
                "value": {
                    "message_id": message_id_0,
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": "irrelevant",
                "value": {
                    "message_id": message_id_1,
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
        ]
    )
    page = blog_page_factory(channel_id="some-id", live_posts=live_posts)

    assert page.get_live_post_index(message_id=message_id_0) == 0
    assert page.get_live_post_index(message_id=message_id_1) == 1
    assert page.get_live_post_index(message_id="does-not-exist") is None


@pytest.mark.django_db
def test_live_page_mixin_get_live_post_by_index(blog_page_factory):
    """Returns the correct live post if given a correct index,
    raises IndexError else."""

    uuid_0 = "906f6590-225f-4204-9e8a-de283f1d173c"
    uuid_1 = "f6d17667-65f8-4202-9051-48f45d71bd2e"
    live_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": uuid_0,
                "value": {
                    "message_id": "some_message_id",
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": uuid_1,
                "value": {
                    "message_id": "other_message_id",
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
        ]
    )
    page = blog_page_factory(channel_id="some-id", live_posts=live_posts)

    block = page.get_live_post_by_index(live_post_index=0)
    assert isinstance(block, StreamValue.StreamChild)
    assert block.id == uuid_0
    assert block.block_type == "live_post"

    block = page.get_live_post_by_index(live_post_index=1)
    assert isinstance(block, StreamValue.StreamChild)
    assert block.id == uuid_1
    assert block.block_type == "live_post"

    with pytest.raises(IndexError):
        # 2 does not exist
        page.get_live_post_by_index(live_post_index=2)


@pytest.mark.django_db
def test_live_page_mixin_get_live_post_by_message_id(blog_page_factory):
    """Returns the correct live post if given a correct message_id,
    raises KeyError else."""

    message_id_0 = "some_message_id"
    message_id_1 = "other_message_id"
    live_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "906f6590-225f-4204-9e8a-de283f1d173c",
                "value": {
                    "message_id": message_id_0,
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": "f6d17667-65f8-4202-9051-48f45d71bd2e",
                "value": {
                    "message_id": message_id_1,
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
        ]
    )
    page = blog_page_factory(channel_id="some-id", live_posts=live_posts)

    block = page.get_live_post_by_message_id(message_id=message_id_0)
    assert isinstance(block, StreamValue.StreamChild)
    assert block.value["message_id"] == message_id_0

    block = page.get_live_post_by_message_id(message_id=message_id_1)
    assert isinstance(block, StreamValue.StreamChild)
    assert block.value["message_id"] == message_id_1

    with pytest.raises(KeyError):
        page.get_live_post_by_message_id(message_id="does-not-exist")


@pytest.mark.django_db
def test_live_page_mixin_add_live_post(blog_page_factory):
    """Adds live post and keeps live posts sorted by creation time."""

    message_id_0 = "some_message_id"
    message_id_1 = "other_message_id"
    live_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "f6d17667-65f8-4202-9051-48f45d71bd2e",
                "value": {
                    "message_id": message_id_1,
                    "created": "9999-01-01T12:00:00",
                    "modified": "9999-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": "906f6590-225f-4204-9e8a-de283f1d173c",
                "value": {
                    "message_id": message_id_0,
                    "created": "2020-01-01T12:00:00",
                    "modified": "2020-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
        ]
    )
    page = blog_page_factory(channel_id="some-id", live_posts=live_posts)

    live_post = construct_live_post_block(message_id="some-id", created=now())
    page.add_live_post(live_post=live_post)
    assert len(page.live_posts) == 3

    live_post = page.get_live_post_by_message_id(message_id="some-id")
    assert isinstance(live_post, StreamValue.StreamChild)
    assert live_post.value["message_id"] == "some-id"

    # It should be inserted between the existing live posts
    assert page.get_live_post_index(message_id="some-id") == 1


@pytest.mark.django_db
def test_live_page_mixin_delete_live_post(blog_page_factory):
    """Deletes a live post if given a valid message_id."""

    message_id_0 = "some_message_id"
    message_id_1 = "other_message_id"
    live_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "irrelevant",
                "value": {
                    "message_id": message_id_0,
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": "irrelevant",
                "value": {
                    "message_id": message_id_1,
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
        ]
    )
    page = blog_page_factory(channel_id="some-id", live_posts=live_posts)
    assert len(page.live_posts) == 2

    page.delete_live_post(message_id=message_id_1)
    assert len(page.live_posts) == 1

    # Already deleted
    with pytest.raises(KeyError):
        page.delete_live_post(message_id=message_id_1)


@pytest.mark.django_db
def test_live_page_mixin_update_live_post(blog_page_factory):
    """Updates modified field when live post is updated."""

    message_id_0 = "some_message_id"
    message_id_1 = "other_message_id"
    live_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "irrelevant",
                "value": {
                    "message_id": message_id_0,
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": "irrelevant",
                "value": {
                    "message_id": message_id_1,
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
        ]
    )
    page = blog_page_factory(channel_id="some-id", live_posts=live_posts)
    live_post = page.get_live_post_by_message_id(message_id=message_id_0)
    page.update_live_post(live_post=live_post)

    live_post = page.get_live_post_by_message_id(message_id=message_id_0)
    diff = now() - live_post.value["modified"]
    assert diff.total_seconds() == pytest.approx(0.0, abs=1)


@pytest.mark.django_db
def test_edit_live_posts_updates_last_updated_at(blog_page_factory):
    """last_updated_at is updated when a live post is added, edited or deleted."""

    page = blog_page_factory(channel_id="some-id")
    last_updated_at = page.last_updated_at
    diff = now() - last_updated_at
    assert diff.total_seconds() == pytest.approx(0.0, abs=1)

    # ADD
    _now = now()
    live_post = construct_live_post_block(message_id="some-id", created=_now)
    page.add_live_post(live_post=live_post)
    assert page.last_updated_at > last_updated_at
    assert page.last_updated_at == _now
    last_updated_at = page.last_updated_at

    # EDIT
    live_post = page.get_live_post_by_index(live_post_index=0)
    page.update_live_post(live_post=live_post)
    assert page.last_updated_at > last_updated_at
    assert page.last_updated_at == live_post.value["modified"]
    last_updated_at = page.last_updated_at

    # DELETE
    page.delete_live_post(message_id="some-id")
    assert page.last_updated_at > last_updated_at
    last_updated_at = page.last_updated_at
    diff = now() - last_updated_at
    assert diff.total_seconds() == pytest.approx(0.0, abs=1)


@pytest.mark.django_db
def test_edit_live_posts_sends_signal(blog_page_factory):
    count = 0
    _channel_id = _renders = _removals = None

    def callback(sender, channel_id, renders, removals, **kwargs):
        nonlocal count, _channel_id, _renders, _removals
        _channel_id, _renders, _removals = channel_id, renders, removals
        count += 1

    live_page_update.connect(callback)
    page = blog_page_factory(channel_id="some-id")

    try:
        # ADD
        live_post = construct_live_post_block(message_id="some-id", created=now())
        page.add_live_post(live_post=live_post)
        live_post = page.get_live_post_by_index(live_post_index=0)
        live_post_id = live_post.id

        assert count == 1
        assert _channel_id == "some-id"
        assert _renders == {
            live_post_id: live_post.render(context={"block_id": live_post_id})
        }
        assert _removals == []

        # EDIT
        page.update_live_post(live_post=live_post)
        assert count == 2
        assert _channel_id == "some-id"
        assert _renders == {
            live_post_id: live_post.render(context={"block_id": live_post_id})
        }
        assert _removals == []

        # DELETE
        page.delete_live_post(message_id="some-id")
        assert count == 3
        assert _channel_id == "some-id"
        assert _renders == {}
        assert _removals == [live_post_id]

    finally:
        live_page_update.disconnect(callback)


@pytest.mark.django_db
def test_get_updates_since(blog_page_factory):
    live_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "1",
                "value": {
                    "message_id": "1",
                    "created": "2021-01-01T12:00:00",
                    "modified": None,
                    "show": True,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": "2",
                "value": {
                    "message_id": "2",
                    "created": "2022-01-01T12:00:00",
                    "modified": "2022-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": "3",
                "value": {
                    "message_id": "3",
                    "created": "2021-01-01T12:00:00",
                    "modified": "2022-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
        ]
    )
    page = blog_page_factory(channel_id="some-id", live_posts=live_posts)
    updated_posts, current_posts = page.get_updates_since(
        last_update_ts=datetime(2021, 2, 1),
    )

    assert current_posts == ["3", "2", "1"]
    assert "2" in updated_posts
    assert "3" in updated_posts
    assert "1" not in updated_posts


@pytest.mark.django_db
def test_get_updates_since_hidden_posts(blog_page_factory):
    live_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "1",
                "value": {
                    "message_id": "1",
                    "created": "2021-01-01T12:00:00",
                    "modified": None,
                    "show": True,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": "2",
                "value": {
                    "message_id": "2",
                    "created": "2022-01-01T12:00:00",
                    "modified": "2022-01-01T12:00:00",
                    "show": False,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": "3",
                "value": {
                    "message_id": "3",
                    "created": "2021-01-01T12:00:00",
                    "modified": "2022-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
        ]
    )

    page = blog_page_factory(channel_id="some-id", live_posts=live_posts)
    updated_posts, current_posts = page.get_updates_since(
        last_update_ts=datetime(2021, 2, 1),
    )

    assert current_posts == ["3", "1"]
    assert "3" in updated_posts
    assert "2" not in updated_posts
    assert "1" not in updated_posts
