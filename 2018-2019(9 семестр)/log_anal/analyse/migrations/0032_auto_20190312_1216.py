# Generated by Django 2.1.3 on 2019-03-12 09:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0031_auto_20190309_0340'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bigrams',
            old_name='category1',
            new_name='domain_category1',
        ),
        migrations.RenameField(
            model_name='bigrams',
            old_name='category2',
            new_name='domain_category2',
        ),
        migrations.RenameField(
            model_name='bigrams',
            old_name='type1',
            new_name='domain_type1',
        ),
        migrations.RenameField(
            model_name='bigrams',
            old_name='type2',
            new_name='domain_type2',
        ),
        migrations.RenameField(
            model_name='trigrams',
            old_name='category1',
            new_name='domain_category1',
        ),
        migrations.RenameField(
            model_name='trigrams',
            old_name='category2',
            new_name='domain_category2',
        ),
        migrations.RenameField(
            model_name='trigrams',
            old_name='category3',
            new_name='domain_category3',
        ),
    ]
