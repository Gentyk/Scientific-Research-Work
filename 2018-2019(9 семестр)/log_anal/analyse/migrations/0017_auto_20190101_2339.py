# Generated by Django 2.1.3 on 2019-01-01 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0016_vectors'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vectors',
            old_name='click',
            new_name='start',
        ),
        migrations.RemoveField(
            model_name='vectors',
            name='star',
        ),
        migrations.AddField(
            model_name='vectors',
            name='username',
            field=models.CharField(db_index=True, default='I', max_length=50),
        ),
    ]
