import pytest

from wagtail_live_debug.receiver import (
    MESSAGE_CREATED,
    MESSAGE_DELETED,
    MESSAGE_EDITED,
    WagtailLiveInterfaceReceiver,
)


@pytest.fixture
def interface_receiver():
    """Wagtail Live Interface Receiver instance."""

    return WagtailLiveInterfaceReceiver("testapp", "SimpleLivePage")


@pytest.fixture
def edited_message(message):
    """An edited message fixture."""

    message["content"] = "Edited"
    return message


def test_interface_receiver_dispatch_new_msg(mocker, message, interface_receiver):
    """Dispatches new message to add_message."""

    mocker.patch.object(interface_receiver, "add_message")
    message["update_type"] = MESSAGE_CREATED
    interface_receiver.dispatch(message)

    interface_receiver.add_message.assert_called_once_with(message=message)


def test_interface_receiver_dispatch_edit_msg(mocker, message, interface_receiver):
    """Dispatches edited message to change_message."""

    mocker.patch.object(interface_receiver, "change_message")
    message["update_type"] = MESSAGE_EDITED
    interface_receiver.dispatch(message)

    interface_receiver.change_message.assert_called_once_with(message=message)


def test_interface_receiver_dispatch_delete_msg(mocker, interface_receiver):
    """Dispatches deleted message to delete_message."""

    mocker.patch.object(interface_receiver, "delete_message")
    message = {
        "id": 1,
        "channel": "test_channel",
        "update_type": MESSAGE_DELETED,
    }
    interface_receiver.dispatch(message)

    interface_receiver.delete_message.assert_called_once_with(message=message)


def test_get_channel_id_from_message(interface_receiver, message):
    """Retrieves channel ID from message."""

    got = interface_receiver.get_channel_id_from_message(message)
    assert got == message["channel"]


def test_get_message_id_from_message(interface_receiver, message):
    """Retrieves message ID from message."""

    got = interface_receiver.get_message_id_from_message(message)
    assert got == message["id"]


def test_get_message_text(interface_receiver, message):
    """Retrieves message text from message."""

    got = interface_receiver.get_message_text(message)
    assert got == message["content"]


def test_get_message_files_if_no_files(interface_receiver, message):
    """Returns empty list if message doesn't contain files."""

    got = interface_receiver.get_message_files(message)
    assert got == []


def test_get_message_files_if_files(interface_receiver, message):
    """Returns list of files if message contains files."""

    message["files"] = ["unrealistic-file"]
    got = interface_receiver.get_message_files(message)
    assert got == ["unrealistic-file"]


def test_get_message_id_from_edited_message(interface_receiver, edited_message):
    """Retrieves message ID from edited message."""

    got = interface_receiver.get_message_id_from_edited_message(edited_message)
    assert got == edited_message["id"]


def test_get_message_text_from_edited_message(interface_receiver, edited_message):
    """Retrieves message text from edited message."""

    got = interface_receiver.get_message_text_from_edited_message(edited_message)
    assert got == "Edited"


def test_get_files_from_edited_message_no_files(interface_receiver, edited_message):
    """Returns empty list if edited message doesn't contain files."""

    got = interface_receiver.get_message_files_from_edited_message(edited_message)
    assert got == []


def test_get_files_from_edited_message_if_files(interface_receiver, edited_message):
    """Returns list of files if edited message contains files."""

    edited_message["files"] = ["unrealistic-file"]
    got = interface_receiver.get_message_files_from_edited_message(edited_message)
    assert got == ["unrealistic-file"]
