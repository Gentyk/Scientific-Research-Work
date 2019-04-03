# Generated by Django 2.1.3 on 2019-04-03 15:14

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0060_collections_num_vectors'),
    ]

    operations = [
        migrations.CreateModel(
            name='VectorsOneVersion2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(db_index=True, default='I', max_length=50)),
                ('type', models.IntegerField(db_index=True, default=0)),
                ('days', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None)),
                ('day_parts', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None)),
                ('activity_time', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), default=list, size=None)),
                ('middle_pause', models.FloatField(default=0)),
                ('middle_pause2', models.FloatField(default=0)),
                ('middle_pause3', models.FloatField(default=0)),
                ('quantity_middle_pause', models.IntegerField(default=0)),
                ('quantity_middle_pause2', models.IntegerField(default=0)),
                ('quantity_middle_pause3', models.IntegerField(default=0)),
                ('start_comp_pause', models.FloatField(default=0)),
                ('urls', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None)),
                ('url_freq_pause', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(default=0), size=None)),
                ('url_maps', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None), size=None)),
                ('domains', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None)),
                ('dom_freq_pause', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(default=0), size=None)),
                ('domain_maps', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None), size=None)),
                ('url_bi', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None)),
                ('url_bi_pauses', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(default=0), size=None)),
                ('dom_bi', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None)),
                ('dom_bi_pauses', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(default=0), size=None)),
                ('url_tri', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None)),
                ('url_tri_pauses', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(default=0), size=None)),
                ('dom_tri', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None)),
                ('dom_tri_pauses', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(default=0), size=None)),
                ('domain_type', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), default=list, size=None)),
                ('domain_categories', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), default=list, size=None)),
                ('last_click', models.IntegerField(default=0)),
                ('collection', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='analyse.Collections')),
            ],
        ),
    ]
