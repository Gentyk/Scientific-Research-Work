# Generated by Django 2.1.3 on 2019-01-01 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0012_auto_20190101_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bigrams',
            name='two_domains',
            field=models.TextField(db_index=True, default=''),
        ),
        migrations.AlterField(
            model_name='trigrams',
            name='three_domains',
            field=models.TextField(db_index=True, default=''),
        ),
    ]
