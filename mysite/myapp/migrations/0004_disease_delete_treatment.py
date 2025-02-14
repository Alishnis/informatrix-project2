# Generated by Django 5.1.4 on 2025-01-16 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0003_ctanalysis"),
    ]

    operations = [
        migrations.CreateModel(
            name="Disease",
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
                ("name", models.CharField(max_length=200)),
                ("symptoms", models.TextField()),
                ("treatment", models.TextField()),
                ("description", models.TextField()),
            ],
        ),
        migrations.DeleteModel(
            name="Treatment",
        ),
    ]
