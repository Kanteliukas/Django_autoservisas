# Generated by Django 3.2.13 on 2022-06-01 18:34

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('autoservisas_app', '0008_auto_20220601_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='description',
            field=tinymce.models.HTMLField(default=''),
        ),
    ]
