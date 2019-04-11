# Generated by Django 2.1.3 on 2019-04-11 15:36

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0068_anomalyml'),
    ]

    operations = [
        migrations.AddField(
            model_name='vectorsoneversion3',
            name='domains_map',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), default=list, size=None),
        ),
        migrations.AddField(
            model_name='vectorsoneversion3',
            name='urls_map',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), default=list, size=None),
        ),
    ]
