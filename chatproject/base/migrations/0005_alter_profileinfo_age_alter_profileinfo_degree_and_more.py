# Generated by Django 4.2.6 on 2023-11-15 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_profileinfo_requests_delete_profileimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profileinfo',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profileinfo',
            name='degree',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='profileinfo',
            name='name',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='profileinfo',
            name='surname',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='profileinfo',
            name='workplace',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]