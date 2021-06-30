from wagtail_live.receivers import BaseMessageReceiver

MESSAGE_CREATED = 1
MESSAGE_EDITED = 2
MESSAGE_DELETED = 3


class WebAppReceiver(BaseMessageReceiver):
    """Webapp receiver."""

    def dispatch_event(self, event):
        """See base class."""

        message = event
        if message["update_type"] == MESSAGE_EDITED:
            self.change_message(message=message)
            return

        elif message["update_type"] == MESSAGE_DELETED:
            self.delete_message(message=message)
            return

        else:
            self.add_message(message=message)

    def get_channel_id_from_message(self, message):
        """See base class."""

        return message["channel"]

    def get_message_id_from_message(self, message):
        """See base class."""

        return message["id"]

    def get_message_text(self, message):
        """See base class."""

        return message["content"]

    def get_message_files(self, message):
        """See base class."""

        return message["files"] if "files" in message else []

    def get_message_id_from_edited_message(self, message):
        """See base class."""

        return self.get_message_id_from_message(message=message)

    def get_message_text_from_edited_message(self, message):
        """See base class."""

        return self.get_message_text(message=message)

    def get_message_files_from_edited_message(self, message):
        """See base class."""

        return self.get_message_files(message=message)
