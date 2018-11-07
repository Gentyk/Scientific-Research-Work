# Generated by Django 2.1.3 on 2018-11-04 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LOG',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateTimeField(db_index=True)),
                ('time', models.DateTimeField()),
                ('url', models.TextField()),
                ('domain', models.CharField(db_index=True, max_length=100)),
                ('window_coordinates', models.CharField(max_length=30)),
                ('cursor_coordinates', models.CharField(max_length=20)),
                ('start_computer', models.BooleanField(db_index=True, default=False)),
                ('seance', models.IntegerField(db_index=True)),
                ('username', models.CharField(db_index=True, max_length=50)),
            ],
        ),
    ]
