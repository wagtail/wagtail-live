import json

import pytest
from wagtail.core.models import Page
from wagtail.images import get_image_model

from tests.testapp.models import BlogPage, LivePageMixin


@pytest.mark.django_db
def test_blog_page_factory(home, blog_page, blog_page_factory):
    """Showcase, let's see what is possible with pytest and factories."""

    # `blog_page` is a BlogPage instance.
    assert BlogPage.objects.count() == 1
    assert isinstance(blog_page, BlogPage)
    assert isinstance(blog_page, LivePageMixin)
    assert blog_page.title == "Page 1"
    assert blog_page.channel_id == "channel-1"

    # `blog_page_factory` is the BlogPageFactory.
    from ..factories import BlogPageFactory  # noqa

    assert blog_page_factory is BlogPageFactory

    # Calling the factory will increment the fields.
    page = blog_page_factory()
    assert page.title == "Page 2"
    assert page.channel_id == "channel-2"

    # You can define fields, if you need something specific
    page = blog_page_factory(title="Foo", channel_id="bar")
    assert page.title == "Foo"
    assert page.channel_id == "bar"

    # `create_batch` to get many pages.
    page_4, page_5, page_6 = blog_page_factory.create_batch(size=3)
    assert page_4.title == "Page 4"
    assert page_5.title == "Page 5"
    assert page_6.title == "Page 6"

    # Use `parent` to add a page to a specific parent page.
    parent = Page(title="Parent")
    # Wagtail/Treebeard way of adding a page to the tree.
    home.add_child(instance=parent)
    # Factory way of adding a page to the tree.
    page = blog_page_factory(title="Child", parent=parent)
    # Note, first `/` is home. The page tree is: Home / Parent / Child
    assert page.url == "/parent/child/"

    page = blog_page_factory(
        live_posts=json.dumps(
            [
                {
                    "type": "live_post",
                    "id": "743fbd4d-929a-4b85-8f30-93cb19d6a933",
                    "value": {
                        "message_id": "my_special_id",
                        "created": "2021-01-01T12:00:00",
                        "modified": "2021-01-01T12:00:00",
                        "show": True,
                        "content": [],
                    },
                }
            ]
        ),
    )
    assert page.live_posts._raw_data == [
        {
            "type": "live_post",
            "id": "743fbd4d-929a-4b85-8f30-93cb19d6a933",
            "value": {
                "message_id": "my_special_id",
                "created": "2021-01-01T12:00:00",
                "modified": "2021-01-01T12:00:00",
                "show": True,
                "content": [],
            },
        }
    ]

    page = blog_page_factory(live_posts_create="all")
    assert get_image_model().objects.count() == 1
    assert page.live_posts._raw_data == [
        {
            "type": "live_post",
            "id": "743fbd4d-929a-4b85-8f30-93cb19d6a933",
            "value": {
                "message_id": "some_message_id",
                "created": "2021-01-01T12:00:00",
                "modified": "2021-01-01T12:00:00",
                "show": 1,
                "content": [
                    {
                        "type": "message",
                        "value": "Text",
                        "id": "f8982691-9d43-4bd5-8ad3-a04314283b54",
                    },
                    {
                        "type": "image",
                        "value": get_image_model().objects.first().id,
                        "id": "13d8a12a-ce8b-452a-9d6f-d18d6cfd4eb5",
                    },
                    {
                        "type": "embed",
                        "value": "https://www.youtube.com/watch?v=s29vaGnFcq8",
                        "id": "d05cafe1-8e54-467d-a72c-8a9c29300395",
                    },
                ],
            },
        }
    ]
