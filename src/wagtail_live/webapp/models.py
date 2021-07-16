""" Webapp models."""

from django.db import models


class Channel(models.Model):
    """A model that mimics a channel in a messaging app."""

    channel_name = models.CharField(
        max_length=124,
        help_text="Channel name",
        primary_key=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of channel creation",
    )

    def __str__(self):
        return f"#{self.channel_name}"

    class Meta:
        ordering = ["-created"]


class Message(models.Model):
    """A model that mimics a message in a messaging app."""

    channel = models.ForeignKey(
        "Channel",
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="Channel this message was posted to.",
    )
    created = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of message creation",
    )
    modified = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time of last update",
    )
    show = models.BooleanField(
        default=True,
        blank=True,
        help_text="Indicates if this message is shown/hidden",
    )
    content = models.TextField(help_text="Content of the message")

    @property
    def images(self):
        return self.files.all()

    class Meta:
        ordering = ["-created"]


class Image(models.Model):
    """A Model that represents an image of a message."""

    image = models.ImageField(help_text="Image of a message")
    message = models.ForeignKey(
        "Message",
        on_delete=models.CASCADE,
        related_name="files",
        help_text="Message this image was posted to.",
    )
