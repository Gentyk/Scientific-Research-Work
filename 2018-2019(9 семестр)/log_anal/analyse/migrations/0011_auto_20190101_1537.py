# Generated by Django 2.1.3 on 2019-01-01 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0010_auto_20190101_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trigrams',
            name='three_domains',
            field=models.CharField(db_index=True, default='', max_length=200),
        ),
    ]
