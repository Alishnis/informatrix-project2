# Generated by Django 5.1.5 on 2025-03-21 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0011_bloodanalysis"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bloodanalysis",
            old_name="glucose_level",
            new_name="erythrocytes_level",
        ),
        migrations.AddField(
            model_name="bloodanalysis",
            name="hematocrit_level",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="bloodanalysis",
            name="thrombocytes_level",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
