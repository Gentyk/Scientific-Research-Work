# Generated by Django 2.1.3 on 2019-04-02 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0058_domains2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collections',
            name='thousand',
        ),
    ]
