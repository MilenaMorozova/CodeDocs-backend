# Generated by Django 3.1.5 on 2021-01-30 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=200, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128, unique=True)),
                ('account_color', models.CharField(max_length=7)),
                ('is_confirmed', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
