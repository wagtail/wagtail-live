from datetime import datetime

import pytest
from django.core.management import call_command

from wagtail_live.blocks import construct_live_post_block

from ..testapp.models import SimpleLivePage


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Loads fixtures into database."""

    with django_db_blocker.unblock():
        call_command("loaddata", "fixtures.json")


@pytest.fixture
def live_post_block():
    """Fixture representing a live post block instance."""

    return construct_live_post_block(
        message_id="1234",
        created=datetime(1970, 1, 1, 12, 00),
    )


@pytest.fixture
def valid_embed_url():
    """A valid embed url."""

    return "https://www.youtube.com/watch?v=Wrc_gofwDR8"


@pytest.fixture
def simple_live_page(db):
    """Fixture representing a SimpleLivePage instance."""

    return SimpleLivePage.objects.first()
