# Generated by Django 3.1.4 on 2021-02-01 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc_tables', '0005_auto_20210201_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='name',
            field=models.CharField(blank=True, default='Без названия', max_length=300, null=True, verbose_name='Названия теста'),
        ),
        migrations.AlterField(
            model_name='user_tests',
            name='count_answer',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]