# Generated by Django 3.2 on 2021-07-02 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("testapp", "0004_regularpage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogpage",
            name="channel_id",
            field=models.CharField(
                blank=True, help_text="Channel ID", max_length=255, unique=True
            ),
        ),
    ]
