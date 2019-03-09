# Generated by Django 2.1.3 on 2019-03-07 10:06

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0026_users_thousand'),
    ]

    operations = [
        migrations.CreateModel(
            name='ML',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team', models.IntegerField(db_index=True)),
                ('clicks', models.IntegerField(default=0)),
                ('num_users', models.IntegerField(default=0)),
                ('patterns', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(default=''), size=None)),
                ('middleFAR', models.FloatField(default=0.0)),
                ('middleFRR', models.FloatField(default=0.0)),
                ('accuracy', models.FloatField(default=0.0)),
            ],
        ),
    ]
