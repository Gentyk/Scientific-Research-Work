# Generated by Django 2.1.3 on 2019-03-30 18:44

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0046_patterns'),
    ]

    operations = [
        migrations.AddField(
            model_name='vectorsoneversion',
            name='activity_time',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), default=[], size=None),
        ),
        migrations.AddField(
            model_name='vectorsoneversion',
            name='last_click',
            field=models.IntegerField(default=0),
        ),
    ]
