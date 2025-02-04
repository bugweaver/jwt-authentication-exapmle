# Generated by Django 5.1.5 on 2025-01-29 08:50

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="username",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="refreshtoken",
            name="token",
            field=models.UUIDField(
                default=uuid.UUID("bd3a8916-5b90-4d80-bfaa-9a8675ad9dca"),
                editable=False,
                unique=True,
            ),
        ),
    ]
