import pytest
from django.urls.resolvers import URLPattern
from django.views import View

from tests.testapp.models import BlogPage
from wagtail_live.publishers.base import PollingPublisherMixin


@pytest.fixture
def polling_mixin():
    return PollingPublisherMixin()


def test_polling_mixin_instance(polling_mixin):
    assert isinstance(polling_mixin, View)


def test_polling_mixin_model(polling_mixin):
    assert polling_mixin.model == BlogPage


def test_get_urls():
    patterns = PollingPublisherMixin.get_urls()
    assert len(patterns) == 1

    pattern = patterns[0]
    assert isinstance(pattern, URLPattern)
    assert pattern.pattern._route == "get-updates/<str:channel_id>/"
    assert pattern.callback.view_class == PollingPublisherMixin
    assert pattern.name == ""


def test_get_last_update_client_from_request(polling_mixin, rf):
    request = rf.get("/", {"last_update_ts": "1000.00"})

    assert polling_mixin.get_last_update_client_from_request(request=request) == 1000.00


def test_post_raise_not_implemented_error(polling_mixin, rf):
    with pytest.raises(NotImplementedError):
        polling_mixin.post(request=rf.post("/"), channel_id=1)


def test_get_raise_not_implemented_error(polling_mixin, rf):
    with pytest.raises(NotImplementedError):
        polling_mixin.get(request=rf.get("/"), channel_id=1)
