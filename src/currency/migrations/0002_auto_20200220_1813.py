# Generated by Django 2.2.10 on 2020-02-20 18:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rate',
            old_name='sell',
            new_name='sale',
        ),
    ]
