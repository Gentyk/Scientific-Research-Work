# Generated by Django 2.1.3 on 2018-11-07 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0002_auto_20181105_0017'),
    ]

    operations = [
        migrations.CreateModel(
            name='Easy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('url', models.TextField(default='')),
            ],
        ),
    ]
