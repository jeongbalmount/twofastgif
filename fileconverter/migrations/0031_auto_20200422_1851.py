# Generated by Django 3.0.4 on 2020-04-22 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileconverter', '0030_auto_20200422_1848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadmodel',
            name='fps_value',
            field=models.IntegerField(default=15),
        ),
        migrations.AlterField(
            model_name='uploadurlmodel',
            name='fps_value',
            field=models.IntegerField(default=15),
        ),
    ]
