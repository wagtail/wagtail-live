import json

import pytest
from django.utils.timezone import now
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks.stream_block import StreamValue
from wagtail.core.models import Page

from tests.testapp.models import BlogPage
from wagtail_live.blocks import construct_live_post_block
from wagtail_live.models import LivePageMixin


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


def test_live_page_mixin_live_posts_is_optional():
    """live_posts field is optional."""

    assert LivePageMixin.live_posts.field.blank is True


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
                "id": "906f6590-225f-4204-9e8a-de283f1d173c",
                "value": {
                    "message_id": message_id_0,
                    "created": "2020-01-01T12:00:00",
                    "modified": "2020-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
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
def test_live_mixin_update_live_posts_creates_revisions(blog_page_factory):
    """Revisions are created when a live post is added, edited or deleted."""

    page = blog_page_factory(channel_id="some-id")
    assert page.revisions.count() == 0

    # ADD
    live_post = construct_live_post_block(message_id="some-id", created=now())
    page.add_live_post(live_post=live_post)
    assert page.revisions.count() == 1
    # The revision is published
    page.refresh_from_db()
    assert page.get_latest_revision() == page.live_revision

    # EDIT
    live_post = page.get_live_post_by_index(live_post_index=0)
    page.update_live_post(live_post=live_post)
    assert page.revisions.count() == 2
    # The revision is published
    page.refresh_from_db()
    assert page.get_latest_revision() == page.live_revision

    # DELETE
    page.delete_live_post(message_id="some-id")
    assert page.revisions.count() == 3
    # The revision is published
    page.refresh_from_db()
    assert page.get_latest_revision() == page.live_revision
