# Generated by Django 5.0.6 on 2025-04-02 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0015_rename_miniappchatstatus_appchatstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='socket_sended',
            field=models.BooleanField(default=False),
        ),
    ]
