# Generated by Django 3.0.4 on 2020-04-07 10:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('fileconverter', '0025_auto_20200406_2143'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadmodel',
            name='uploadedFiles',
        ),
        migrations.AddField(
            model_name='uploadmodel',
            name='first_uploaded_file',
            field=models.FileField(default=django.utils.timezone.now, upload_to='first/%Y/%m/%d/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uploadmodel',
            name='second_uploaded_file',
            field=models.FileField(blank=True, upload_to='second/%Y/%m/%d/'),
        ),
    ]
