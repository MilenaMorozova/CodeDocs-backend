# Generated by Django 3.1.5 on 2021-02-09 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20210130_1153'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='is_confirmed',
            new_name='is_active',
        ),
    ]
