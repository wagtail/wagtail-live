from datetime import datetime

import pytest
from rest_framework import serializers


@pytest.fixture
def message():
    return {
        "id": 1,
        "channel": "test_channel",
        "created": serializers.DateTimeField().to_representation(
            datetime(1970, 1, 1, 12, 00),
        ),
        "modified": None,
        "show": True,
        "content": "Some content.",
    }
