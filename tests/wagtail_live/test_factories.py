import pytest
from wagtail.core.models import Site

from tests.testapp.models import BlogPage, LivePageMixin


@pytest.mark.django_db
def test_home_fixture(home):
    assert home == Site.objects.first().root_page


@pytest.mark.django_db
def test_blog_page_factory_instance(blog_page):
    assert BlogPage.objects.count() == 1
    assert isinstance(blog_page, BlogPage)
    assert isinstance(blog_page, LivePageMixin)
    assert blog_page.title.startswith("Page ")
    assert blog_page.channel_id.startswith("channel-")


@pytest.mark.django_db
def test_blog_page_factory_factory(blog_page_factory):
    assert BlogPage.objects.count() == 0
    blog_page = blog_page_factory(title="Some Title", channel_id="some-id")
    assert isinstance(blog_page, BlogPage)
    assert isinstance(blog_page, LivePageMixin)
    assert blog_page.title == "Some Title"
    assert blog_page.channel_id == "some-id"
    assert BlogPage.objects.count() == 1
