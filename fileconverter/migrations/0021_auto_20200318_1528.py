# Generated by Django 3.0.4 on 2020-03-18 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileconverter', '0020_auto_20200318_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadurlmodel',
            name='uploadURL',
            field=models.URLField(null=True),
        ),
    ]
