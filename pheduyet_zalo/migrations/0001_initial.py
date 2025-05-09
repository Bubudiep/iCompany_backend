# Generated by Django 5.1.7 on 2025-05-06 10:12

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ZaloUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zalo_id', models.CharField(blank=True, max_length=20, null=True)),
                ('zalo_phone', models.CharField(blank=True, max_length=13, null=True)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Zalo Accounts',
                'verbose_name_plural': 'Zalo Accounts',
            },
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('isGroup', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount_approver', models.ManyToManyField(blank=True, related_name='amount_approver_member', to='pheduyet_zalo.zalouser')),
                ('approver', models.ManyToManyField(blank=True, related_name='approver_member', to='pheduyet_zalo.zalouser')),
                ('host', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pheduyet_zalo.zalouser')),
                ('member', models.ManyToManyField(blank=True, related_name='group_member', to='pheduyet_zalo.zalouser')),
                ('payment_approver', models.ManyToManyField(blank=True, related_name='payment_approver_member', to='pheduyet_zalo.zalouser')),
            ],
            options={
                'verbose_name': 'Group approver',
                'verbose_name_plural': 'Group approver',
            },
        ),
        migrations.CreateModel(
            name='ApproveType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=250, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approver', models.ManyToManyField(blank=True, related_name='type_approver_to', to='pheduyet_zalo.zalouser')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pheduyet_zalo.zalouser')),
            ],
        ),
        migrations.CreateModel(
            name='ApproveItemRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(blank=True, choices=[('create', 'Chờ duyệt'), ('approve', 'Duyệt'), ('disburse', 'Giải ngân'), ('cancel', 'Hủy'), ('complete', 'Hoàn thành'), ('reject', 'Từ chối')], max_length=100, null=True)),
                ('comment', models.TextField(blank=True, max_length=1000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pheduyet_zalo.zalouser')),
            ],
        ),
        migrations.CreateModel(
            name='ApproveItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=250, null=True)),
                ('picture_base64', models.TextField(blank=True, null=True)),
                ('picture_link', models.CharField(blank=True, max_length=250, null=True)),
                ('amount', models.IntegerField(default=0)),
                ('status', models.CharField(blank=True, choices=[('pending', 'Chờ duyệt'), ('approved', 'Đã duyệt'), ('disbursed', 'Đã giải ngân'), ('complete', 'Hoàn thành'), ('cancel', 'Hủy'), ('reject', 'Từ chối')], max_length=100, null=True)),
                ('rate', models.IntegerField(default=0)),
                ('feedback', models.CharField(blank=True, max_length=250, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('types', models.ManyToManyField(blank=True, to='pheduyet_zalo.approvetype')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pheduyet_zalo.usergroup')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pheduyet_zalo.zalouser')),
                ('sendto', models.ManyToManyField(blank=True, related_name='send_approver_to', to='pheduyet_zalo.zalouser')),
            ],
        ),
    ]
