# Generated by Django 5.1.7 on 2025-03-29 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_userprofile_avatar_base64'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
