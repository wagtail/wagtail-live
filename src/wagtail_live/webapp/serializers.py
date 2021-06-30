"""Webapp serializers."""

from rest_framework import serializers

from .models import DummyChannel, Message


class DummyChannelSerializer(serializers.ModelSerializer):
    """DummyChannel serializer"""

    class Meta:
        model = DummyChannel
        fields = ["channel_name", "created"]


class MessageSerializer(serializers.ModelSerializer):
    """Message serializer"""

    class Meta:
        model = Message
        fields = ["id", "channel", "created", "modified", "show", "content"]
