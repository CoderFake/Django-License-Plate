# Generated by Django 4.2.5 on 2023-10-31 14:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("camera", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="carmanagement",
            name="plate_img",
            field=models.BinaryField(null=True),
        ),
    ]
