# Generated by Django 2.2 on 2020-03-10 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileconverter', '0009_remove_uploadmodel_filenames'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadmodel',
            name='uploadedFiles',
            field=models.FileField(upload_to='uploadedFiles/%Y/%m/%d/'),
        ),
    ]