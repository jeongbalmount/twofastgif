# Generated by Django 3.0.4 on 2020-05-19 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileconverter', '0041_auto_20200519_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadmodel',
            name='scaleValue_select_1',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='uploadmodel',
            name='scaleValue_select_2',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
