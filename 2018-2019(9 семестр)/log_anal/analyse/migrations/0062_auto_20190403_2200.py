# Generated by Django 2.1.3 on 2019-04-03 19:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0061_vectorsoneversion2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='combinemls',
            name='collection',
        ),
        migrations.DeleteModel(
            name='BaseCollections',
        ),
        migrations.DeleteModel(
            name='CombineMLs',
        ),
    ]
