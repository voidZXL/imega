# Generated by Django 2.2.7 on 2019-11-25 13:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0007_auto_20191113_1753'),
    ]

    operations = [
        migrations.RenameField(
            model_name='album',
            old_name='description',
            new_name='desc',
        ),
        migrations.RenameField(
            model_name='photo',
            old_name='description',
            new_name='desc',
        ),
    ]
