# Generated by Django 5.1.7 on 2025-06-16 08:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0057_companyoperator_import_raw'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyvendor',
            name='is_sub',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='companyvendor',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='company.companyvendor'),
        ),
    ]
