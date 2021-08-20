# Generated by Django 3.2.4 on 2021-06-22 06:46

import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("wagtailcore", "0060_fix_workflow_unique_constraint"),
    ]

    operations = [
        migrations.CreateModel(
            name="BlogPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "channel_id",
                    models.CharField(help_text="Channel ID", max_length=255),
                ),
                (
                    "last_update_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Date and time of the last update for this channel/page",
                        null=True,
                    ),
                ),
                (
                    "live_posts",
                    wagtail.core.fields.StreamField(
                        [
                            (
                                "live_post",
                                wagtail.core.blocks.StructBlock(
                                    [
                                        (
                                            "message_id",
                                            wagtail.core.blocks.CharBlock(
                                                help_text="Message's ID"
                                            ),
                                        ),
                                        (
                                            "created",
                                            wagtail.core.blocks.DateTimeBlock(
                                                help_text="Date and time of message creation"
                                            ),
                                        ),
                                        (
                                            "modified",
                                            wagtail.core.blocks.DateTimeBlock(
                                                blank=True,
                                                help_text="Date and time of last update",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "show",
                                            wagtail.core.blocks.BooleanBlock(
                                                default=True,
                                                help_text="Indicates if this message is shown/hidden",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "content",
                                            wagtail.core.blocks.StreamBlock(
                                                [
                                                    (
                                                        "text",
                                                        wagtail.core.blocks.RichTextBlock(
                                                            help_text="Text of the message"
                                                        ),
                                                    ),
                                                    (
                                                        "image",
                                                        wagtail.images.blocks.ImageChooserBlock(
                                                            help_text="Image of the message"
                                                        ),
                                                    ),
                                                    (
                                                        "embed",
                                                        wagtail.embeds.blocks.EmbedBlock(
                                                            help_text="URL of the embed message"
                                                        ),
                                                    ),
                                                ]
                                            ),
                                        ),
                                    ]
                                ),
                            )
                        ],
                        blank=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page", models.Model),
        ),
    ]
