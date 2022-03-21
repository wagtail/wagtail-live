import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from tests.utils import clear_function_cache_before_and_after_execution
from wagtail_live.utils import (
    get_live_page_model,
    get_live_post_block,
    get_live_receiver,
)


@override_settings(WAGTAIL_LIVE_PAGE_MODEL="")
def test_get_live_page_model_setting_missing():
    expected_err = "You haven't specified a live page model in your settings."
    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_live_page_model()


@override_settings(WAGTAIL_LIVE_PAGE_MODEL="tests.testapp.models.RegularPage")
def test_get_live_page_model_bad_model():
    expected_err = (
        "The live page model tests.testapp.models.RegularPage doesn't inherit from "
        "wagtail_live.models.LivePageMixin."
    )
    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_live_page_model()


@override_settings(WAGTAIL_LIVE_RECEIVER="tests.testapp.receivers.DummyReceiver")
def test_get_live_receiver_bad_receiver():
    expected_err = (
        "The receiver tests.testapp.receivers.DummyReceiver doesn't inherit from "
        "wagtail_live.receivers.BaseMessageReceiver."
    )
    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_live_receiver()


@clear_function_cache_before_and_after_execution(cached_func=get_live_post_block)
@override_settings(WAGTAIL_LIVE_POST_BLOCK="tests.testapp.blocks.CustomBlock")
def test_get_custom_live_post_block_bad_block():
    expected_err = (
        "The block tests.testapp.blocks.CustomBlock doesn't inherit from "
        "wagtail_live.blocks.LivePostBlock."
    )
    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_live_post_block()
