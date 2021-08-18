"""Wagtail Live Exceptions."""


class RequestVerificationError(Exception):
    """A incoming request couldn't be verified."""

    pass


class WebhookSetupError(Exception):
    """An error occured while setting a webhook connection with the input source."""

    pass
