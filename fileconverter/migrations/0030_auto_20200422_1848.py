# Generated by Django 3.0.4 on 2020-04-22 09:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('fileconverter', '0029_auto_20200422_1847'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadmodel',
            name='fps_value',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uploadurlmodel',
            name='fps_value',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]