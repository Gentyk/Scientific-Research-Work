# Generated by Django 2.1.3 on 2019-01-01 13:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0013_auto_20190101_1545'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bigrams',
            name='two_domains',
        ),
        migrations.RemoveField(
            model_name='bigrams',
            name='two_urls',
        ),
        migrations.RemoveField(
            model_name='trigrams',
            name='three_domains',
        ),
        migrations.RemoveField(
            model_name='trigrams',
            name='three_urls',
        ),
    ]
