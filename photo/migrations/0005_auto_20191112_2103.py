# Generated by Django 2.2.7 on 2019-11-12 13:03

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0004_auto_20191110_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='cover',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='covered_album', to='photo.Photo'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='album',
            name='create_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='album',
            name='edit_date',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='album',
            name='total_size',
            field=models.PositiveIntegerField(default=3584645),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='can_download',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='photo',
            name='create_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
