# Generated by Django 4.2.11 on 2024-04-16 19:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_queue_lodgement_size"),
    ]

    operations = [
        migrations.AddField(
            model_name="lodgement",
            name="name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]