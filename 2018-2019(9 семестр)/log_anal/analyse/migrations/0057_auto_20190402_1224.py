# Generated by Django 2.1.3 on 2019-04-02 09:24

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0056_auto_20190402_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vectorsoneversion1',
            name='domain_categories',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='vectorsoneversion1',
            name='domain_type',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), default=list, size=None),
        ),
    ]
