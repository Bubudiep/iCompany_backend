# Generated by Django 5.1.7 on 2025-05-07 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pheduyet_zalo', '0013_usergrouprecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergrouprecord',
            name='detail',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
