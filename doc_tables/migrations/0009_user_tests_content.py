# Generated by Django 3.1.4 on 2021-02-07 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc_tables', '0008_auto_20210205_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_tests',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
    ]
