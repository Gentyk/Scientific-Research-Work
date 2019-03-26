# Generated by Django 2.1.3 on 2019-03-26 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0043_auto_20190325_2159'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collections',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team', models.IntegerField(db_index=True)),
                ('thousand', models.IntegerField(db_index=True, default=0)),
                ('users_quantity', models.IntegerField(db_index=True, default=0)),
                ('number_parts_per_day', models.IntegerField(default=0)),
                ('clicks', models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='ml',
            name='clicks',
        ),
        migrations.RemoveField(
            model_name='ml',
            name='num_users',
        ),
        migrations.RemoveField(
            model_name='ml',
            name='team',
        ),
        migrations.RemoveField(
            model_name='vectorsoneversion',
            name='clicks',
        ),
        migrations.RemoveField(
            model_name='vectorsoneversion',
            name='number_parts_per_day',
        ),
        migrations.RemoveField(
            model_name='vectorsoneversion',
            name='team',
        ),
        migrations.RemoveField(
            model_name='vectorsoneversion',
            name='thousand',
        ),
        migrations.AddField(
            model_name='ml',
            name='collection',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='analyse.Collections'),
        ),
        migrations.AddField(
            model_name='vectorsoneversion',
            name='collection',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='analyse.Collections'),
        ),
    ]
