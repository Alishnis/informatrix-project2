# Generated by Django 5.1.5 on 2025-03-20 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0006_analysisct_analysisskin"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="disease",
            name="symptoms",
        ),
    ]
