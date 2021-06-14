import threading

from .receiver import WagtailLiveInterfaceReceiver


class WagtailLiveInterfacePublisher:
    """Wagtail Live Interface Publisher.

    This class sends new updates to the Wagtail Live Interface receiver
    when a message is posted/edited/deleted in the live interface.
    """

    def __init__(self, app_name, model_name):
        """Initializes the receiver which will handle new updates."""

        self.receiver = WagtailLiveInterfaceReceiver(app_name, model_name)

    def deliver(self, update):
        """Delivers a new update to the receiver.

        Args:
            update (dict): update to send
        """

        self.receiver.dispatch(message=update)

    def send_update(self, update_type, data):
        """Formats the update to send and starts a new thread to deliver it.
        
            update_type (int):
                Type of update: 1:CREATED, 2:EDITED or 3:DELETED
            data (dict):
                Data of the update
        """

        data["update_type"] = update_type
        publisher = threading.Thread(target=self.deliver, kwargs={"update": data})
        publisher.start()
