import json

import pytest
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks.stream_block import StreamValue
from wagtail.core.models import Page

from tests.testapp.models import BlogPage
from wagtail_live.models import LivePageMixin


@pytest.mark.django_db
def test_live_page_mixin():
    # LivePageMixin is an abstract model, and cannot be instantiated.
    # We use the `BlogPage` instead.
    assert isinstance(BlogPage(), (LivePageMixin, Page))
    assert hasattr(LivePageMixin, "panels")
    assert isinstance(LivePageMixin.panels[0], FieldPanel)
    assert LivePageMixin.panels[0].field_name == "channel_id"
    assert isinstance(LivePageMixin.panels[1], StreamFieldPanel)
    assert LivePageMixin.panels[1].field_name == "live_posts"
    assert LivePageMixin._meta.abstract is True


def test_live_page_mixin_channel_id_is_optional():
    assert LivePageMixin.channel_id.field.blank is True


def test_live_page_mixin_live_posts_is_optional():
    assert LivePageMixin.live_posts.field.blank is True


@pytest.mark.django_db
def test_live_page_mixin_get_live_post_index(blog_page_factory):
    message_id_0 = "some_message_id"
    message_id_1 = "other_message_id"
    life_posts = json.dumps(
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
    page = blog_page_factory(channel_id="some-id", live_posts=life_posts)
    assert page.get_live_post_index(message_id_0) == 0
    assert page.get_live_post_index(message_id_1) == 1
    # TODO: better return None (do nothing or return) as Python interprets -1 as a True-ish value.
    assert page.get_live_post_index("does-not-exist") == -1


@pytest.mark.django_db
def test_live_page_mixin_get_live_post_by_index(blog_page_factory):
    uuid_0 = "906f6590-225f-4204-9e8a-de283f1d173c"
    uuid_1 = "f6d17667-65f8-4202-9051-48f45d71bd2e"
    life_posts = json.dumps(
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
    page = blog_page_factory(channel_id="some-id", live_posts=life_posts)

    block = page.get_live_post_by_index(0)
    assert isinstance(block, StreamValue.StreamChild)
    assert block.id == uuid_0
    assert block.block_type == "live_post"

    block = page.get_live_post_by_index(1)
    assert isinstance(block, StreamValue.StreamChild)
    assert block.id == uuid_1
    assert block.block_type == "live_post"

    with pytest.raises(IndexError):
        # 2 does not exist
        page.get_live_post_by_index(2)


@pytest.mark.django_db
def test_live_page_mixin_get_live_post_by_message_id(blog_page_factory):
    message_id_0 = "some_message_id"
    message_id_1 = "other_message_id"
    life_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "906f6590-225f-4204-9e8a-de283f1d173c",
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
                "id": "f6d17667-65f8-4202-9051-48f45d71bd2e",
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
    page = blog_page_factory(channel_id="some-id", live_posts=life_posts)

    block = page.get_live_post_by_message_id(message_id_0)
    assert isinstance(block, StreamValue.StreamChild)
    assert block.value["message_id"] == message_id_0

    block = page.get_live_post_by_message_id(message_id_1)
    assert isinstance(block, StreamValue.StreamChild)
    assert block.value["message_id"] == message_id_1

    with pytest.raises(KeyError):
        page.get_live_post_by_message_id("does-not-exist")


@pytest.mark.skip(reason="TODO / Exercise")
def test_live_page_mixin_add_live_post():
    pass


@pytest.mark.skip(reason="TODO / Exercise")
def test_live_page_mixin_delete_live_post():
    pass


@pytest.mark.skip(reason="TODO / Exercise")
def test_live_page_mixin_update_live_post():
    pass


@pytest.mark.django_db
def test_live_mixin_update_live_posts_creates_revisions(blog_page_factory):
    life_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "743fbd4d-929a-4b85-8f30-93cb19d6a933",
                "value": {
                    "message_id": "some_message_id",
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            }
        ]
    )
    page = blog_page_factory(channel_id="some-id", live_posts=life_posts)
    assert page.revisions.count() == 0

    # TODO Update, revision count should be +1

    # Delete
    page.delete_live_post("some_message_id")
    assert page.revisions.count() == 1

    # TODO Add, revision count should be +1
