# Generated by Django 4.2.7 on 2023-11-30 06:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('super_admin', '0001_initial'),
        ('notes', '0002_sellernotes_note_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellernotes',
            name='note_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='super_admin.notetype'),
        ),
    ]