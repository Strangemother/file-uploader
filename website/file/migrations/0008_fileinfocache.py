# Generated by Django 4.2.11 on 2024-04-27 20:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('file', '0007_options_max_file_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileInfoCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_upload_count', models.IntegerField(default=0)),
                ('total_upload_bytes', models.BigIntegerField(blank=True, default=0, null=True)),
                ('total_download_count', models.IntegerField(default=0)),
                ('total_download_bytes', models.BigIntegerField(blank=True, default=0, null=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
