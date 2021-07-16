"""Webapp serializers."""

from rest_framework import serializers

from .models import Channel, Image, Message


class ImageListSerializer(serializers.ListSerializer):
    def get_value(self, dictionary):
        if hasattr(dictionary, "getlist"):
            images = dictionary.getlist("images")
        else:
            images = dictionary.get("images")

        if not images or not images[0]:
            return
        return [{"image": item} for item in images]


class ImageSerializer(serializers.ModelSerializer):
    """Image serializer"""

    class Meta:
        model = Image
        fields = ["image"]
        list_serializer_class = ImageListSerializer

    def to_representation(self, instance):
        image = instance.image
        return {
            "id": instance.id,
            "image": {
                "name": image.name,
                "url": image.url,
                "width": image.width,
                "height": image.height,
            },
        }


class MessageSerializer(serializers.ModelSerializer):
    """Message serializer"""

    images = ImageSerializer(many=True, allow_null=True)

    class Meta:
        model = Message
        fields = ["id", "channel", "created", "modified", "show", "content", "images"]

    def create(self, validated_data):
        images = validated_data.pop("images")
        message = Message.objects.create(**validated_data)

        if images:
            for image in images:
                Image.objects.create(message=message, **image)

        return message

    def update(self, instance, validated_data):
        images = validated_data.pop("images")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if images:
            for image in images:
                Image.objects.create(message=instance, **image)

        instance.save()
        return instance


class ChannelSerializer(serializers.ModelSerializer):
    """Channel serializer"""

    class Meta:
        model = Channel
        fields = ["channel_name", "created"]
