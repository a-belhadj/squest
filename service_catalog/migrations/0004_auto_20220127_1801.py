# Generated by Django 3.2.11 on 2022-01-27 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0003_instance_date_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestmessage',
            name='content',
            field=models.TextField(default='no content', verbose_name='Message'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='supportmessage',
            name='content',
            field=models.TextField(default='no content', verbose_name='Message'),
            preserve_default=False,
        ),
    ]
