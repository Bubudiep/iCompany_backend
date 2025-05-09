# Generated by Django 5.1.7 on 2025-05-06 12:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pheduyet_zalo', '0002_zalouser_isadmin'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastCheckGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_check', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pheduyet_zalo.usergroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pheduyet_zalo.zalouser')),
            ],
        ),
        migrations.CreateModel(
            name='ZaloUserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, max_length=13, null=True)),
                ('avatar_base64', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pheduyet_zalo.zalouser')),
            ],
        ),
    ]
