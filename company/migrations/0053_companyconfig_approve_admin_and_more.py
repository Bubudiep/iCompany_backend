# Generated by Django 5.1.7 on 2025-05-28 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0052_companyconfig_admin_can_payout_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyconfig',
            name='approve_admin',
            field=models.ManyToManyField(blank=True, related_name='list_admin_approve', to='company.companystaff'),
        ),
        migrations.AlterField(
            model_name='advancerequesthistory',
            name='action',
            field=models.CharField(choices=[('update', 'Cập nhập'), ('edit', 'Chỉnh sửa'), ('create', 'Tạo mới'), ('retrieve', 'Hoàn ngân'), ('payout', 'Giải ngân'), ('cancel', 'Hủy bỏ'), ('pending', 'Chờ duyệt'), ('approved', 'Đã duyệt'), ('rejected', 'Từ chối')], default='pending', max_length=10),
        ),
    ]
