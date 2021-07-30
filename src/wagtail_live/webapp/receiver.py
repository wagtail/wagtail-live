from wagtail_live.receivers.base import BaseMessageReceiver

from .models import Image

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

        return message["images"]

    def get_image_title(self, image):
        """See base class."""

        return image["image"]["name"].split(".")[0].replace("-", " ")

    def get_image_name(self, image):
        """See base class."""

        return image["image"]["name"]

    def get_image_mimetype(self, image):
        """See base class."""

        mime_type = image["image"]["name"].split(".")[-1]
        return "jpeg" if mime_type == "jpg" else mime_type

    def get_image_dimensions(self, image):
        """See base class."""

        return (image["image"]["width"], image["image"]["height"])

    def get_image_content(self, image):
        """See base class."""

        return Image.objects.get(id=image["id"]).image

    def get_message_id_from_edited_message(self, message):
        """See base class."""

        return self.get_message_id_from_message(message=message)

    def get_message_text_from_edited_message(self, message):
        """See base class."""

        return self.get_message_text(message=message)

    def get_message_files_from_edited_message(self, message):
        """See base class."""

        return self.get_message_files(message=message)
