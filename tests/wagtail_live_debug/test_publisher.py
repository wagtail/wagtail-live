import pytest

from wagtail_live_debug.publisher import WagtailLiveInterfacePublisher
from wagtail_live_debug.receiver import (
    MESSAGE_CREATED,
    WagtailLiveInterfaceReceiver,
)


@pytest.fixture
def interface_publisher():
    """Wagtail Live interface publisher instance."""

    return WagtailLiveInterfacePublisher("testapp", "SimpleLivePage")


def test_interface_publisher_receiver(interface_publisher):
    """Receiver is an instance of WagtailLiveInerfaceReceiver."""

    assert isinstance(interface_publisher.receiver, WagtailLiveInterfaceReceiver)


def test_interface_publisher_deliver(interface_publisher, message, mocker):
    """Delivers a new update by calling receiver's dispatch method."""

    mocker.patch.object(WagtailLiveInterfaceReceiver, "dispatch")
    interface_publisher.deliver(message)

    WagtailLiveInterfaceReceiver.dispatch.assert_called_once_with(message=message)


def test_interface_publisher_send_update(interface_publisher, message, mocker):
    """Forms a new update and delivers it."""

    mocker.patch.object(WagtailLiveInterfacePublisher, "deliver")
    interface_publisher.send_update(update_type=MESSAGE_CREATED, data=message)
    message["update_type"] = MESSAGE_CREATED

    WagtailLiveInterfacePublisher.deliver.assert_called_once_with(update=message)
