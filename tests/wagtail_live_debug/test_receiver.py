import pytest

from wagtail_live_debug.receiver import (
    MESSAGE_CREATED,
    MESSAGE_DELETED,
    MESSAGE_EDITED,
    WagtailLiveInterfaceReceiver,
)


@pytest.fixture
def interface_receiver():
    return WagtailLiveInterfaceReceiver("testapp", "SimpleLivePage")


@pytest.fixture
def edited_message(message):
    message["content"] = "Edited"
    return message


def test_interface_receiver_dispatch_new_msg(mocker, message, interface_receiver):
    mocker.patch.object(WagtailLiveInterfaceReceiver, "add_message")
    message["update_type"] = MESSAGE_CREATED
    interface_receiver.dispatch(message)
    WagtailLiveInterfaceReceiver.add_message.assert_called_once_with(message=message)


def test_interface_receiver_dispatch_edit_msg(mocker, message, interface_receiver):
    mocker.patch.object(WagtailLiveInterfaceReceiver, "change_message")
    message["update_type"] = MESSAGE_EDITED
    interface_receiver.dispatch(message)
    WagtailLiveInterfaceReceiver.change_message.assert_called_once_with(message=message)


def test_interface_receiver_dispatch_delete_msg(mocker, interface_receiver):
    mocker.patch.object(WagtailLiveInterfaceReceiver, "delete_message")
    message = {
        "id": 1,
        "channel": "test_channel",
        "update_type": MESSAGE_DELETED,
    }
    interface_receiver.dispatch(message)
    WagtailLiveInterfaceReceiver.delete_message.assert_called_once_with(message=message)


def test_get_channel_id_from_message(interface_receiver, message):
    got = interface_receiver.get_channel_id_from_message(message)
    assert got == message["channel"]


def test_get_message_id_from_message(interface_receiver, message):
    got = interface_receiver.get_message_id_from_message(message)
    assert got == message["id"]


def test_get_message_text(interface_receiver, message):
    got = interface_receiver.get_message_text(message)
    assert got == message["content"]


def test_get_message_files_if_no_files(interface_receiver, message):
    got = interface_receiver.get_message_files(message)
    assert got == []


def test_get_message_files_if_files(interface_receiver, message):
    message["files"] = ["unrealistic-file"]
    got = interface_receiver.get_message_files(message)
    assert got == ["unrealistic-file"]


def test_get_message_id_from_edited_message(interface_receiver, edited_message):
    got = interface_receiver.get_message_id_from_edited_message(edited_message)
    assert got == edited_message["id"]


def test_get_message_text_from_edited_message(interface_receiver, edited_message):
    got = interface_receiver.get_message_text_from_edited_message(edited_message)
    assert got == "Edited"


def test_get_files_from_edited_message_no_files(interface_receiver, edited_message):
    got = interface_receiver.get_message_files_from_edited_message(edited_message)
    assert got == []


def test_get_files_from_edited_message_if_files(interface_receiver, edited_message):
    edited_message["files"] = ["unrealistic-file"]
    got = interface_receiver.get_message_files_from_edited_message(edited_message)
    assert got == ["unrealistic-file"]
