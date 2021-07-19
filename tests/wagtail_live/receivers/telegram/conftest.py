import pytest


@pytest.fixture
def telegram_message():
    return {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {
                "id": 100,
                "is_bot": False,
                "first_name": "Tester",
            },
            "chat": {"id": 100, "first_name": "Tester", "type": "private"},
            "date": 1626555185,
            "text": (
                "This a message.\n"
                "Some content here but not much...\n"
                "And some other content.\n"
                "This post contains only text."
            ),
        },
    }


@pytest.fixture
def telegram_channel_post():
    return {
        "update_id": 2,
        "channel_post": {
            "message_id": 2,
            "sender_chat": {"id": -100, "title": "test_channel", "type": "channel"},
            "chat": {"id": -100, "title": "test_channel", "type": "channel"},
            "date": 1626555153,
            "text": (
                "This is a channel post.\n"
                "Some content here but not much...\n"
                "And some other content.\n"
                "This post contains only text."
            ),
        },
    }


@pytest.fixture
def telegram_embed_message():
    return {
        "update_id": 3,
        "message": {
            "message_id": 3,
            "from": {
                "id": 100,
                "is_bot": False,
                "first_name": "Tester",
            },
            "chat": {"id": 100, "first_name": "Tester", "type": "private"},
            "date": 1626555312,
            "text": (
                "This is another test post.\n"
                "This post contains an embed.\n"
                "https://www.youtube.com/watch?v=Cq3LOsf2kSY\n"
                "It also contains emojis : \ud83d\ude00\ud83d\udc4b"
            ),
            "entities": [{"offset": 56, "length": 43, "type": "url"}],
        },
    }


@pytest.fixture
def telegram_embed_message_2():
    return {
        "update_id": 10,
        "message": {
            "message_id": 10,
            "from": {
                "id": 100,
                "is_bot": False,
                "first_name": "Tester",
            },
            "chat": {"id": 100, "first_name": "Tester", "type": "private"},
            "date": 1626569872,
            "text": (
                "This is another test post.\n"
                "https://www.youtube.com/watch?v=Cq3LOsf2kSY. Some content here.\n"
                "Some content here. https://www.youtube.com/watch?v=Cq3LOsf2kSY"
            ),
            "entities": [
                {"offset": 27, "length": 43, "type": "url"},
                {"offset": 110, "length": 43, "type": "url"},
            ],
        },
    }


@pytest.fixture
def telegram_edited_message():
    return {
        "update_id": 4,
        "edited_message": {
            "message_id": 3,
            "from": {
                "id": 100,
                "is_bot": False,
                "first_name": "Tester",
            },
            "chat": {"id": 100, "first_name": "Tester", "type": "private"},
            "date": 1626555312,
            "edit_date": 1626555391,
            "text": (
                "This is another test post that has been edited.\n"
                "This post contains an embed.\n"
                "https://www.youtube.com/watch?v=Cq3LOsf2kSY\n"
                "It also contains emojis : \ud83d\ude00\ud83d\udc4b"
            ),
            "entities": [{"offset": 77, "length": 43, "type": "url"}],
        },
    }


@pytest.fixture
def telegram_edited_channel_post():
    return {
        "update_id": 5,
        "edited_channel_post": {
            "message_id": 2,
            "sender_chat": {"id": -100, "title": "test_channel", "type": "channel"},
            "chat": {"id": -100, "title": "test_channel", "type": "channel"},
            "date": 1626555153,
            "edit_date": 1626556460,
            "text": (
                "This a channel post that has been edited.\n"
                "Some content here but not much...\n"
                "And some other content.\n"
                "This post contains only text."
            ),
        },
    }


@pytest.fixture
def telegram_image_message():
    return {
        "update_id": 6,
        "message": {
            "message_id": 6,
            "from": {
                "id": 100,
                "is_bot": False,
                "first_name": "Tester",
            },
            "chat": {"id": 100, "first_name": "Tester", "type": "private"},
            "date": 1626555489,
            "photo": [
                {
                    "file_id": "cwADIAQ",
                    "file_unique_id": "AQADGLQxG1yRmVN4",
                    "file_size": 955,
                    "width": 90,
                    "height": 55,
                },
                {
                    "file_id": "bQADIAQ",
                    "file_unique_id": "AQADGLQxG1yRmVNy",
                    "file_size": 9967,
                    "width": 320,
                    "height": 195,
                },
                {
                    "file_id": "eAADIAQ",
                    "file_unique_id": "AQADGLQxG1yRmVN9",
                    "file_size": 31254,
                    "width": 750,
                    "height": 457,
                },
            ],
            "caption": "This is an image message.",
        },
    }


@pytest.fixture
def telegram_media_message_1():
    return {
        "update_id": 7,
        "message": {
            "message_id": 7,
            "from": {
                "id": 100,
                "is_bot": False,
                "first_name": "Tester",
            },
            "chat": {"id": 100, "first_name": "Tester", "type": "private"},
            "date": 1626555527,
            "media_group_id": "13",
            "photo": [
                {
                    "file_id": "cwADIAQ",
                    "file_unique_id": "AQADGLQxG1yRmVN4",
                    "file_size": 955,
                    "width": 90,
                    "height": 55,
                },
                {
                    "file_id": "bQADIAQ",
                    "file_unique_id": "AQADGLQxG1yRmVNy",
                    "file_size": 9967,
                    "width": 320,
                    "height": 195,
                },
                {
                    "file_id": "eAADIAQ",
                    "file_unique_id": "AQADGLQxG1yRmVN9",
                    "file_size": 31254,
                    "width": 750,
                    "height": 457,
                },
            ],
            "caption": "This is a media image.",
        },
    }


@pytest.fixture
def telegram_media_message_2():
    return {
        "update_id": 8,
        "message": {
            "message_id": 8,
            "from": {
                "id": 100,
                "is_bot": False,
                "first_name": "Tester",
            },
            "chat": {"id": 100, "first_name": "Tester", "type": "private"},
            "date": 1626555527,
            "media_group_id": "13",
            "photo": [
                {
                    "file_id": "CAANzAAMgBA",
                    "file_unique_id": "AQADGbQxG1yRmVN4",
                    "file_size": 669,
                    "width": 90,
                    "height": 44,
                },
                {
                    "file_id": "CAANtAAMgBA",
                    "file_unique_id": "AQADGbQxG1yRmVNy",
                    "file_size": 5775,
                    "width": 320,
                    "height": 156,
                },
                {
                    "file_id": "CAAN4AAMgBA",
                    "file_unique_id": "AQADGbQxG1yRmVN9",
                    "file_size": 21242,
                    "width": 800,
                    "height": 389,
                },
                {
                    "file_id": "CAAN5AAMgBA",
                    "file_unique_id": "AQADGbQxG1yRmVN-",
                    "file_size": 43307,
                    "width": 1280,
                    "height": 622,
                },
            ],
        },
    }


@pytest.fixture
def telegram_message_with_entities():
    return {
        "update_id": 9,
        "message": {
            "message_id": 9,
            "from": {
                "id": 100,
                "is_bot": False,
                "first_name": "Tester",
            },
            "chat": {"id": 100, "first_name": "Tester", "type": "private"},
            "date": 1626555917,
            "text": (
                "This post contains different type of entities.\n"
                "This is a regular link https://github.com/.\n"
                "This is a hashtag entity #WagtailLiveBot\n"
                "This is a link_text wagtail."
            ),
            "entities": [
                {"offset": 70, "length": 19, "type": "url"},
                {"offset": 116, "length": 15, "type": "hashtag"},
                {
                    "offset": 152,
                    "length": 7,
                    "type": "text_link",
                    "url": "https://github.com/wagtail",
                },
            ],
        },
    }
