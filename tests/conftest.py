import pytest
from wagtail.core.models import Site

from .factories import BlogPageFactory
from pytest_factoryboy import register

register(BlogPageFactory)


@pytest.fixture
def home():
    # Root page is created by Wagtail migrations.
    return Site.objects.first().root_page
