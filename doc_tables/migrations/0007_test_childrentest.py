# Generated by Django 3.1.4 on 2021-02-05 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc_tables', '0006_auto_20210201_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='childrenTest',
            field=models.ManyToManyField(blank=True, related_name='_test_childrenTest_+', to='doc_tables.Test'),
        ),
    ]
