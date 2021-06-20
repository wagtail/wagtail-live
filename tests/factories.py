import json

import wagtail_factories
import factory

from tests.testapp.models import BlogPage


class BlogPageFactory(wagtail_factories.PageFactory):
    title = factory.Sequence(lambda n: "Page {}".format(n))
    channel_id = factory.Sequence(lambda n: "channel-{}".format(n))

    class Meta:
        model = BlogPage

    # https://factoryboy.readthedocs.io/en/stable/reference.html#factory.post_generation
    @factory.post_generation
    def live_posts_create(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted == "live_post":
            # Only the live_post block, no content.
            self.live_posts = json.dumps(
                [
                    {
                        "type": "live_post",
                        "id": "743fbd4d-929a-4b85-8f30-93cb19d6a933",
                        "value": {
                            "message_id": "some_message_id",
                            "created": "2021-01-01T12:00:00",
                            "modified": "2021-01-01T12:00:00",
                            "show": wagtail_factories.ImageChooserBlockFactory().id,
                            "content": [],
                        },
                    }
                ]
            )
        if extracted == "all":
            # live_post block, with all possible content
            self.live_posts = json.dumps(
                [
                    {
                        "type": "live_post",
                        "id": "743fbd4d-929a-4b85-8f30-93cb19d6a933",
                        "value": {
                            "message_id": "some_message_id",
                            "created": "2021-01-01T12:00:00",
                            "modified": "2021-01-01T12:00:00",
                            "show": wagtail_factories.ImageChooserBlockFactory().id,
                            "content": [
                                {
                                    "type": "message",
                                    "value": "Text",
                                    "id": "f8982691-9d43-4bd5-8ad3-a04314283b54",
                                },
                                {
                                    "type": "image",
                                    "value": 1,
                                    "id": "13d8a12a-ce8b-452a-9d6f-d18d6cfd4eb5",
                                },
                                {
                                    "type": "embed",
                                    "value": "https://www.youtube.com/watch?v=s29vaGnFcq8",
                                    "id": "d05cafe1-8e54-467d-a72c-8a9c29300395",
                                },
                            ],
                        },
                    }
                ]
            )
        elif extracted == "message":
            # live_post block, with only the message block.  TODO: rename `message` to `text`.
            self.live_posts = json.dumps(
                [
                    {
                        "type": "live_post",
                        "id": "743fbd4d-929a-4b85-8f30-93cb19d6a933",
                        "value": {
                            "message_id": "some_message_id",
                            "created": "2021-01-01T12:00:00",
                            "modified": "2021-01-01T12:00:00",
                            "show": True,
                            "content": [
                                {
                                    "type": "message",
                                    "value": "Text",
                                    "id": "f8982691-9d43-4bd5-8ad3-a04314283b54",
                                },
                            ],
                        },
                    }
                ]
            )
        elif extracted == "image":
            # live_post block, with only the image block.
            self.live_posts = json.dumps(
                [
                    {
                        "type": "live_post",
                        "id": "743fbd4d-929a-4b85-8f30-93cb19d6a933",
                        "value": {
                            "message_id": "some_message_id",
                            "created": "2021-01-01T12:00:00",
                            "modified": "2021-01-01T12:00:00",
                            "show": True,
                            "content": [
                                {
                                    "type": "image",
                                    "value": 1,
                                    "id": "13d8a12a-ce8b-452a-9d6f-d18d6cfd4eb5",
                                },
                            ],
                        },
                    }
                ]
            )
        elif extracted == "embed":
            # live_post block, with only the embed block.
            self.live_posts = json.dumps(
                [
                    {
                        "type": "live_post",
                        "id": "743fbd4d-929a-4b85-8f30-93cb19d6a933",
                        "value": {
                            "message_id": "some_message_id",
                            "created": "2021-01-01T12:00:00",
                            "modified": "2021-01-01T12:00:00",
                            "show": True,
                            "content": [
                                {
                                    "type": "embed",
                                    "value": "https://www.youtube.com/watch?v=s29vaGnFcq8",
                                    "id": "d05cafe1-8e54-467d-a72c-8a9c29300395",
                                },
                            ],
                        },
                    }
                ]
            )

        self.save()
