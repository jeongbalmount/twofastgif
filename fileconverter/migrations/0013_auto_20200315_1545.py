# Generated by Django 2.2 on 2020-03-15 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileconverter', '0012_uploadmodel_uploadbyurl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadmodel',
            name='uploadedFiles',
            field=models.FileField(blank=True, upload_to=''),
        ),
    ]