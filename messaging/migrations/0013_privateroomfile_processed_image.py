# Generated by Django 4.2.7 on 2023-11-26 09:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("messaging", "0012_alter_privateroomfile_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="privateroomfile",
            name="processed_image",
            field=models.ImageField(
                blank=True, null=True, upload_to="processed_images/"
            ),
        ),
    ]
