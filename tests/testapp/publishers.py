from wagtail_live.publishers.websocket import BaseWebsocketPublisher


class DummyWebsocketPublisher(BaseWebsocketPublisher):
    def publish(self, channel_id, renders, removals):
        pass


class DummyPublisher:
    pass
