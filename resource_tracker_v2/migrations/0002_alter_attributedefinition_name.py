# Generated by Django 3.2.13 on 2023-05-26 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resource_tracker_v2', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attributedefinition',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
