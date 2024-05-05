# Generated by Django 4.2.11 on 2024-04-26 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file', '0005_fileunit_download_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='Options',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_default', models.BooleanField(default=False)),
                ('allocated_size', models.IntegerField(default=1, help_text='Gigabyte Units')),
            ],
        ),
    ]
