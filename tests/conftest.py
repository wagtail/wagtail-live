import pytest
from pytest_factoryboy import register
from wagtail.core.models import Site

from .factories import BlogPageFactory

register(BlogPageFactory)


@pytest.fixture
def home():
    # Root page is created by Wagtail migrations.
    return Site.objects.first().root_page
