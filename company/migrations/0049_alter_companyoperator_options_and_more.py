# Generated by Django 5.1.7 on 2025-05-28 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0048_alter_operatorworkhistory_end_date_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='companyoperator',
            options={'ordering': ['-id'], 'verbose_name': 'Operator 1 List', 'verbose_name_plural': 'Operator 1 List'},
        ),
        migrations.AlterModelOptions(
            name='operatorupdatehistory',
            options={'ordering': ['-changed_at'], 'verbose_name': 'Operator 2 Update History', 'verbose_name_plural': 'Operator 2 Update Histories'},
        ),
        migrations.AlterModelOptions(
            name='operatorworkhistory',
            options={'ordering': ['-id'], 'verbose_name': 'Operator 3 Working History', 'verbose_name_plural': 'Operator 3 Working Histories'},
        ),
    ]
