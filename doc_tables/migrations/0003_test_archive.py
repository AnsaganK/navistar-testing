# Generated by Django 3.1.4 on 2021-01-29 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc_tables', '0002_user_tests_anonym_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='archive',
            field=models.BooleanField(default=False),
        ),
    ]
