# Generated by Django 2.1.3 on 2019-03-12 09:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0032_auto_20190312_1216'),
    ]

    operations = [
        migrations.RenameField(
            model_name='domains',
            old_name='category',
            new_name='domain_category',
        ),
        migrations.RenameField(
            model_name='domains',
            old_name='type',
            new_name='domain_type',
        ),
        migrations.RenameField(
            model_name='trigrams',
            old_name='type1',
            new_name='domain_type1',
        ),
        migrations.RenameField(
            model_name='trigrams',
            old_name='type2',
            new_name='domain_type2',
        ),
        migrations.RenameField(
            model_name='trigrams',
            old_name='type3',
            new_name='domain_type3',
        ),
    ]
