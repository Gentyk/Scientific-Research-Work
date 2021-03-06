# Generated by Django 2.1.3 on 2019-03-12 21:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0036_auto_20190313_0000'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clicks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analyse.Domains')),
                ('url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analyse.URLs')),
            ],
        ),
        migrations.RemoveField(
            model_name='bigrams',
            name='domain1',
        ),
        migrations.RemoveField(
            model_name='bigrams',
            name='domain2',
        ),
        migrations.RemoveField(
            model_name='bigrams',
            name='time1',
        ),
        migrations.RemoveField(
            model_name='bigrams',
            name='time2',
        ),
        migrations.RemoveField(
            model_name='bigrams',
            name='url1',
        ),
        migrations.RemoveField(
            model_name='bigrams',
            name='url2',
        ),
        migrations.RemoveField(
            model_name='log',
            name='domain',
        ),
        migrations.RemoveField(
            model_name='log',
            name='time',
        ),
        migrations.RemoveField(
            model_name='log',
            name='url',
        ),
        migrations.RemoveField(
            model_name='trigrams',
            name='domain1',
        ),
        migrations.RemoveField(
            model_name='trigrams',
            name='domain2',
        ),
        migrations.RemoveField(
            model_name='trigrams',
            name='domain3',
        ),
        migrations.RemoveField(
            model_name='trigrams',
            name='time1',
        ),
        migrations.RemoveField(
            model_name='trigrams',
            name='time2',
        ),
        migrations.RemoveField(
            model_name='trigrams',
            name='time3',
        ),
        migrations.RemoveField(
            model_name='trigrams',
            name='url1',
        ),
        migrations.RemoveField(
            model_name='trigrams',
            name='url2',
        ),
        migrations.RemoveField(
            model_name='trigrams',
            name='url3',
        ),
        migrations.AddField(
            model_name='bigrams',
            name='click1',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='first_click_in_bi', to='analyse.Clicks'),
        ),
        migrations.AddField(
            model_name='bigrams',
            name='click2',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='second_click_in_bi', to='analyse.Clicks'),
        ),
        migrations.AddField(
            model_name='log',
            name='click',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='analyse.Clicks'),
        ),
        migrations.AddField(
            model_name='trigrams',
            name='click1',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='first_click_in_tri', to='analyse.Clicks'),
        ),
        migrations.AddField(
            model_name='trigrams',
            name='click2',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='second_click_in_tri', to='analyse.Clicks'),
        ),
        migrations.AddField(
            model_name='trigrams',
            name='click3',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='third_click_in_tri', to='analyse.Clicks'),
        ),
    ]
