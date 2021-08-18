import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from wagtail_live.utils import get_live_page_model, get_live_receiver


@override_settings(WAGTAIL_LIVE_PAGE_MODEL="")
def test_get_live_page_model_setting_missing():
    expected_err = "You haven't specified a live page model in your settings."
    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_live_page_model()


@override_settings(WAGTAIL_LIVE_PAGE_MODEL="tests.testapp.models.RegularPage")
def test_get_live_page_model_bad_model():
    expected_err = (
        "The live page model specified doesn't inherit from "
        "wagtail_live.models.LivePageMixin."
    )
    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_live_page_model()


@override_settings(WAGTAIL_LIVE_RECEIVER="tests.testapp.receivers.DummyReceiver")
def test_get_live_receiver_bad_receiver():
    expected_err = (
        "The receiver tests.testapp.receivers.DummyReceiver doesn't inherit from "
        + "wagtail_live.receivers.BaseMessageReceiver."
    )
    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_live_receiver()
