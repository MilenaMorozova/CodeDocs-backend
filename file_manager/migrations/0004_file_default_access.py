# Generated by Django 3.1.5 on 2021-04-07 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_manager', '0003_operations'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='default_access',
            field=models.IntegerField(choices=[(0, 'Viewer'), (1, 'Editor'), (2, 'Owner')], default=0),
        ),
    ]