# Generated by Django 4.2.6 on 2023-11-13 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='upload_date',
            field=models.DateTimeField(),
        ),
    ]