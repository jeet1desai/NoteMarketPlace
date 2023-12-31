# Generated by Django 4.2.7 on 2023-11-30 06:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('super_admin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SellerNotes',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('admin_remark', models.CharField(blank=True, max_length=500, null=True)),
                ('published_date', models.DateTimeField(blank=True, null=True)),
                ('title', models.CharField(max_length=100)),
                ('display_picture', models.CharField(max_length=500)),
                ('number_of_pages', models.IntegerField(default=0)),
                ('description', models.CharField(max_length=500)),
                ('university_name', models.CharField(blank=True, max_length=200, null=True)),
                ('course', models.CharField(blank=True, max_length=100, null=True)),
                ('course_code', models.CharField(blank=True, max_length=100, null=True)),
                ('professor', models.CharField(blank=True, max_length=100, null=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('selling_price', models.IntegerField(default=0)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Draft')], default=1)),
                ('notes_preview', models.CharField(max_length=500)),
                ('file_name', models.CharField(max_length=100)),
                ('file', models.CharField(max_length=500)),
                ('file_size', models.IntegerField(default=0)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_date', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('actioned_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='actioned_notes', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='super_admin.notecategory')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='super_admin.country')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_notes', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='modified_notes', to=settings.AUTH_USER_MODEL)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='seller_notes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
