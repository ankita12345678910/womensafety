# Generated by Django 5.1.3 on 2025-04-02 12:34

import django.db.models.deletion
import django_mysql.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Camera",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("ip_address", models.CharField(max_length=100, unique=True)),
                (
                    "status",
                    django_mysql.models.EnumField(
                        choices=[
                            ("active", "Active"),
                            ("inactive", "Inactive"),
                            ("deleted", "Deleted"),
                        ]
                    ),
                ),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now_add=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cameras",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "viewers",
                    models.ManyToManyField(
                        related_name="viewable_cameras", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "db_table": "cameras",
            },
        ),
    ]
