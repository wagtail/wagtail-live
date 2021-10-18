# Generated by Django 3.2.8 on 2021-10-18 05:34

import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("testapp", "0006_blogpage_last_updated_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogpage",
            name="live_posts",
            field=wagtail.core.fields.StreamField(
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
                                        help_text="Date and time of message creation",
                                        required=False,
                                    ),
                                ),
                                (
                                    "modified",
                                    wagtail.core.blocks.DateTimeBlock(
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
    ]
