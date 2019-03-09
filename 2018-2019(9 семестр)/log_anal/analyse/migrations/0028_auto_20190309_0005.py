# Generated by Django 2.1.3 on 2019-03-08 21:05

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0027_ml'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='domain_category',
            field=models.TextField(db_index=True, default=''),
        ),
        migrations.AddField(
            model_name='log',
            name='domain_type',
            field=models.TextField(db_index=True, default=''),
        ),
        migrations.AddField(
            model_name='users',
            name='frequent_domains_type',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(default=''), default=[], size=None),
        ),
    ]
