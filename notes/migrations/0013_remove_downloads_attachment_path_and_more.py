# Generated by Django 4.2.7 on 2023-12-06 11:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0012_alter_sellernotes_country_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='downloads',
            name='attachment_path',
        ),
        migrations.RemoveField(
            model_name='downloads',
            name='is_paid',
        ),
        migrations.RemoveField(
            model_name='downloads',
            name='purchased_price',
        ),
    ]
