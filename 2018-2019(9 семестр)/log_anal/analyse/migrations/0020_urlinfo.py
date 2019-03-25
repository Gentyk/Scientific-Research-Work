# Generated by Django 2.1.3 on 2019-02-11 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0019_log_thousand'),
    ]

    operations = [
        migrations.CreateModel(
            name='URLInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField(default='')),
                ('type', models.TextField(db_index=True, default='')),
                ('category', models.TextField(db_index=True, default='')),
            ],
        ),
    ]
