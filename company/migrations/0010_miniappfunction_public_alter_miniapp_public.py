# Generated by Django 5.0.6 on 2025-04-02 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0009_alter_miniapp_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='miniappfunction',
            name='public',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='miniapp',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
