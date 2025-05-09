# Generated by Django 5.1.7 on 2025-03-30 04:03

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0007_rename_name_companystaff_cardid_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MiniApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appID', models.CharField(blank=True, max_length=200, null=True, unique=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('isActive', models.BooleanField(blank=True, default=False, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('public', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='MiniAppPricing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='VND', max_length=10)),
                ('duration_in_days', models.PositiveIntegerField(default=30)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('mini_app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pricings', to='company.miniapp')),
            ],
        ),
        migrations.CreateModel(
            name='MiniAppFunction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('mini_app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='functions', to='company.miniapp')),
            ],
            options={
                'unique_together': {('mini_app', 'code')},
            },
        ),
        migrations.CreateModel(
            name='MiniAppRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registered_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('approved', models.BooleanField(default=False)),
                ('note', models.TextField(blank=True, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='app_registrations', to='company.company')),
                ('mini_app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='company.miniapp')),
            ],
            options={
                'unique_together': {('mini_app', 'company')},
            },
        ),
        migrations.CreateModel(
            name='MiniAppSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('is_confirmed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='miniapp_schedules', to='company.company')),
                ('mini_app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='company.miniapp')),
            ],
            options={
                'unique_together': {('mini_app', 'company', 'start_date', 'end_date')},
            },
        ),
    ]
