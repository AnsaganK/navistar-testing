# Generated by Django 3.1.4 on 2021-01-29 08:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('doc_tables', '0003_test_archive'),
    ]

    operations = [
        migrations.RenameField(
            model_name='test',
            old_name='content',
            new_name='content_1',
        ),
        migrations.AddField(
            model_name='test',
            name='content_data',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='test',
            name='unique_slug',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='test', to='doc_tables.testuuid'),
        ),
    ]
