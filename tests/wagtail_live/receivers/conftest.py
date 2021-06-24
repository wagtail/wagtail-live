import pytest


@pytest.fixture
def slack_message():
    return {
        "token": "token",
        "event": {
            "client_msg_id": "some-id",
            "type": "message",
            "text": (
                "This a test post.\n"
                "Some content here but not much...\n"
                "And some other content.\n"
                "This post contains only text."
            ),
            "user": "tester",
            "ts": "1623319199.002300",
            "channel": "slack_channel",
            "event_ts": "1623319199.002300",
            "channel_type": "channel",
        },
        "type": "event_callback",
        "event_id": "Ev024MBEK6F4",
        "event_time": 1623319199,
    }


@pytest.fixture
def slack_embed_message():
    return {
        "token": "token",
        "event": {
            "client_msg_id": "some-id",
            "type": "message",
            "text": (
                "This is another test post.\n"
                "This post contains an embed.\n"
                "<https://www.youtube.com/watch?v=Cq3LOsf2kSY>\n"
                "It also contains emojis :white_check_mark::pray:"
            ),
            "user": "tester",
            "ts": "1623319472.003700",
            "channel": "slack_channel",
            "event_ts": "1623319472.003700",
            "channel_type": "channel",
        },
        "type": "event_callback",
        "event_id": "Ev024MJ8PQHH",
        "event_time": 1623319472,
    }


@pytest.fixture
def slack_edited_message():
    return {
        "token": "token",
        "event": {
            "type": "message",
            "subtype": "message_changed",
            "hidden": True,
            "message": {
                "client_msg_id": "some-id",
                "type": "message",
                "text": (
                    "This is another test post that has been edited.\n"
                    "This post contains an embed.\n"
                    "<https://www.youtube.com/watch?v=Cq3LOsf2kSY>\n"
                    "It also contains emojis :white_check_mark::pray:"
                ),
                "user": "tester",
                "edited": {"user": "tester", "ts": "1623319716.000000"},
                "ts": "1623319472.003700",
            },
            "channel": "slack_channel",
            "previous_message": {
                "client_msg_id": "some-id",
                "type": "message",
                "text": (
                    "This is another test post.\n"
                    "This post contains an embed.\n"
                    "<https://www.youtube.com/watch?v=Cq3LOsf2kSY>\n"
                    "It also contains emojis :white_check_mark::pray:"
                ),
                "user": "tester",
                "ts": "1623319472.003700",
            },
            "event_ts": "1623319716.004600",
            "ts": "1623319716.004600",
            "channel_type": "channel",
        },
        "type": "event_callback",
        "event_id": "Ev024EJWV75L",
        "event_time": 1623319716,
    }


@pytest.fixture
def slack_deleted_message():
    return {
        "token": "token",
        "event": {
            "type": "message",
            "subtype": "message_deleted",
            "hidden": True,
            "deleted_ts": "1623319472.003700",
            "channel": "slack_channel",
            "previous_message": {
                "client_msg_id": "some-id",
                "type": "message",
                "text": (
                    "This is another test post that has been edited.\n"
                    "This post contains an embed.\n"
                    "<https://www.youtube.com/watch?v=Cq3LOsf2kSY>\n"
                    "It also contains emojis :white_check_mark::pray:"
                ),
                "user": "tester",
                "ts": "1623319472.003700",
                "edited": {"user": "tester", "ts": "1623319716.000000"},
            },
            "event_ts": "1623319754.004700",
            "ts": "1623319754.004700",
            "channel_type": "channel",
        },
        "type": "event_callback",
        "event_id": "Ev024MJQH63D",
        "event_time": 1623319754,
    }


@pytest.fixture
def slack_image_message():
    return {
        "token": "token",
        "event": {
            "type": "message",
            "text": ("This is another test post.\n" "This post contains an image."),
            "files": [
                {
                    "id": "1",
                    "created": 1623319567,
                    "timestamp": 1623319567,
                    "name": "test_image.png",
                    "title": "test_image.png",
                    "mimetype": "image/png",
                    "filetype": "png",
                    "pretty_type": "PNG",
                    "user": "tester",
                    "editable": False,
                    "size": 1024203,
                    "mode": "hosted",
                    "is_external": False,
                    "external_type": "",
                    "is_public": True,
                    "public_url_shared": False,
                    "display_as_bot": False,
                    "username": "",
                    "url_private": "https://files.slack.com/files-pri/token/test_image.png",
                    "url_private_download": (
                        "https://files.slack.com/token/download/test_image.png"
                    ),
                    "thumb_64": "https://files.slack.com/files-tmb/token/test_image_64.png",
                    "thumb_80": "https://files.slack.com/files-tmb/token/test_image_80.png",
                    "thumb_360": "https://files.slack.com/files-tmb/token/test_image_360.png",
                    "thumb_360_w": 360,
                    "thumb_360_h": 120,
                    "thumb_480": "https://files.slack.com/files-tmb/token/test_image_480.png",
                    "thumb_480_w": 480,
                    "thumb_480_h": 160,
                    "thumb_160": "https://files.slack.com/files-tmb/token/test_image_160.png",
                    "thumb_720": "https://files.slack.com/files-tmb/token/test_image_720.png",
                    "thumb_720_w": 720,
                    "thumb_720_h": 240,
                    "thumb_800": "https://files.slack.com/files-tmb/token/test_image_800.png",
                    "thumb_800_w": 800,
                    "thumb_800_h": 267,
                    "thumb_960": "https://files.slack.com/files-tmb/token/test_image_960.png",
                    "thumb_960_w": 960,
                    "thumb_960_h": 320,
                    "thumb_1024": "https://files.slack.com/files-tmb/token/test_image_1024.png",
                    "thumb_1024_w": 1024,
                    "thumb_1024_h": 341,
                    "original_w": 3000,
                    "original_h": 1000,
                    "thumb_tiny": "AwAQADC6aaacaaasBppppxppoAaaaacaaaYH/9k=",
                    "permalink": "https://wagtaillive.slack.com/files/test_image.png",
                    "permalink_public": "https://slack-files.com/token-024420f8bb",
                    "has_rich_preview": False,
                }
            ],
            "upload": False,
            "user": "tester",
            "display_as_bot": False,
            "ts": "1623319579.004300",
            "channel": "slack_channel",
            "subtype": "file_share",
            "event_ts": "1623319579.004300",
            "channel_type": "channel",
        },
        "type": "event_callback",
        "event_id": "Ev024TH0PVS8",
        "event_time": 1623319579,
    }


@pytest.fixture
def slack_edited_image_message():
    return {
        "token": "token",
        "event": {
            "type": "message",
            "subtype": "message_changed",
            "hidden": True,
            "message": {
                "type": "message",
                "text": (
                    "This is another test post.\n"
                    "This post contains an image. "
                    "It's been edited."
                ),
                "files": [
                    {
                        "id": "1",
                        "created": 1623319567,
                        "timestamp": 1623319567,
                        "name": "test_image.png",
                        "title": "test_image.png",
                        "mimetype": "image/png",
                        "filetype": "png",
                        "pretty_type": "PNG",
                        "user": "tester",
                        "editable": False,
                        "size": 1024203,
                        "mode": "hosted",
                        "is_external": False,
                        "external_type": "",
                        "is_public": True,
                        "public_url_shared": False,
                        "display_as_bot": False,
                        "username": "",
                        "url_private": (
                            "https://files.slack.com/files-pri/T023G8L63FS/test_image.png"
                        ),
                        "url_private_download": (
                            "https://files.slack.com/files-pri/T023G8L63FS/download/test_image.png"
                        ),
                        "thumb_64": "https://files.slack.com/files-tmb/test_image_64.png",
                        "thumb_80": "https://files.slack.com/files-tmb/test_image_80.png",
                        "thumb_360": "https://files.slack.com/files-tmb/test_image_360.png",
                        "thumb_360_w": 360,
                        "thumb_360_h": 120,
                        "thumb_480": "https://files.slack.com/files-tmb/test_image_480.png",
                        "thumb_480_w": 480,
                        "thumb_480_h": 160,
                        "thumb_160": "https://files.slack.com/files-tmb/test_image_160.png",
                        "thumb_720": "https://files.slack.com/files-tmb/test_image_720.png",
                        "thumb_720_w": 720,
                        "thumb_720_h": 240,
                        "thumb_800": "https://files.slack.com/files-tmb/test_image_800.png",
                        "thumb_800_w": 800,
                        "thumb_800_h": 267,
                        "thumb_960": "https://files.slack.com/files-tmb/test_image_960.png",
                        "thumb_960_w": 960,
                        "thumb_960_h": 320,
                        "thumb_1024": "https://files.slack.com/files-tmb/test_image_1024.png",
                        "thumb_1024_w": 1024,
                        "thumb_1024_h": 341,
                        "original_w": 3000,
                        "original_h": 1000,
                        "thumb_tiny": "AwAQADC6aaacaaasBppppxppoAaaaacaaaYH/9k=",
                        "permalink": "https://wagtaillive.slack.com/files/tester/test_image.png",
                        "permalink_public": "https://slack-files.com/",
                        "has_rich_preview": False,
                    }
                ],
                "upload": False,
                "user": "tester",
                "display_as_bot": False,
                "edited": {"user": "tester", "ts": "1623326006.000000"},
                "ts": "1623319579.004300",
            },
            "channel": "slack_channel",
            "previous_message": {
                "type": "message",
                "text": ("This is another test post.\n" "This post contains an image."),
                "files": [
                    {
                        "id": "1",
                        "created": 1623319567,
                        "timestamp": 1623319567,
                        "name": "test_image.png",
                        "title": "test_image.png",
                        "mimetype": "image/png",
                        "filetype": "png",
                        "pretty_type": "PNG",
                        "user": "tester",
                        "editable": False,
                        "size": 1024203,
                        "mode": "hosted",
                        "is_external": False,
                        "external_type": "",
                        "is_public": True,
                        "public_url_shared": False,
                        "display_as_bot": False,
                        "username": "",
                        "url_private": (
                            "https://files.slack.com/files-pri/T023G8L63FS/test_image.png"
                        ),
                        "url_private_download": (
                            "https://files.slack.com/files-pri/T023G8L63FS/download/test_image.png"
                        ),
                        "thumb_64": "https://files.slack.com/files-tmb/test_image_64.png",
                        "thumb_80": "https://files.slack.com/files-tmb/test_image_80.png",
                        "thumb_360": "https://files.slack.com/files-tmb/test_image_360.png",
                        "thumb_360_w": 360,
                        "thumb_360_h": 120,
                        "thumb_480": "https://files.slack.com/files-tmb/test_image_480.png",
                        "thumb_480_w": 480,
                        "thumb_480_h": 160,
                        "thumb_160": "https://files.slack.com/files-tmb/test_image_160.png",
                        "thumb_720": "https://files.slack.com/files-tmb/test_image_720.png",
                        "thumb_720_w": 720,
                        "thumb_720_h": 240,
                        "thumb_800": "https://files.slack.com/files-tmb/test_image_800.png",
                        "thumb_800_w": 800,
                        "thumb_800_h": 267,
                        "thumb_960": "https://files.slack.com/files-tmb/test_image_960.png",
                        "thumb_960_w": 960,
                        "thumb_960_h": 320,
                        "thumb_1024": "https://files.slack.com/files-tmb/test_image_1024.png",
                        "thumb_1024_w": 1024,
                        "thumb_1024_h": 341,
                        "original_w": 3000,
                        "original_h": 1000,
                        "thumb_tiny": "AwAQADC6aaacaaasBppppxppoAaaaacaaaYH/9k=",
                        "permalink": "https://wagtaillive.slack.com/files/tester/test_image.png",
                        "permalink_public": "https://slack-files.com/",
                        "is_starred": False,
                        "has_rich_preview": False,
                    }
                ],
                "upload": False,
                "user": "tester",
                "display_as_bot": False,
                "ts": "1623319579.004300",
            },
            "event_ts": "1623326006.004800",
            "ts": "1623326006.004800",
            "channel_type": "channel",
        },
        "type": "event_callback",
        "event_id": "Ev024EUE74NA",
        "event_time": 1623326006,
    }
