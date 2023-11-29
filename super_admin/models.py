from django.db import models
from django.utils import timezone
from django.conf import settings

class SystemConfigurations(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=100, null=False, blank=False)
    phone_number = models.CharField(max_length=15, null=False, blank=False)
    profile_picture = models.CharField(max_length=1000000, null=True, blank=True)
    note_picture = models.CharField(max_length=1000000, null=True, blank=True)
    facebook_url = models.URLField(max_length=255, null=True, blank=True)
    twitter_url = models.URLField(max_length=255, null=True, blank=True)
    linkedIn_url = models.URLField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=False, blank=False, related_name='system_configurations_created')

class Country(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=False)
    code = models.CharField(max_length=100, unique=True, null=False)
    created_date = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=False, blank=False, related_name='created_countries')
    modified_date = models.DateTimeField()
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=False, blank=False, related_name='modified_countries')
    is_active = models.BooleanField(default=True)

class NoteCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=False)
    description = models.CharField(max_length=255, null=False)
    created_date = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=False, blank=False, related_name='created_note_categories')
    modified_date = models.DateTimeField()
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=False, blank=False, related_name='modified_note_categories')
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:  # If the instance is being created
            self.CreatedDate = timezone.now()
        self.ModifiedDate = timezone.now()
        super().save(*args, **kwargs)

class NoteType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=False)
    description = models.CharField(max_length=255, null=False)
    created_date = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=False, blank=False, related_name='created_note_types')
    modified_date = models.DateTimeField()
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=False, blank=False, related_name='modified_note_types')
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:  # If the instance is being created
            self.CreatedDate = timezone.now()
        self.ModifiedDate = timezone.now()
        super().save(*args, **kwargs)


