# Generated by Django 4.2.6 on 2023-11-01 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='user',
            field=models.CharField(),
        ),
    ]