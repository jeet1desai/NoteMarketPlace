from django.contrib import admin
from .models import SystemConfigurations, Country, NoteCategory, NoteType

# Register your models here.
# admin.site.register(SystemConfigurations)
@admin.register(SystemConfigurations)
class UserModel(admin.ModelAdmin):
    list_display = ("id", "email", "created_date", "created_by")

@admin.register(Country)
class UserModel(admin.ModelAdmin):
    list_display = ("id", "name", "code", "is_active")


@admin.register(NoteCategory)
class UserModel(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")


@admin.register(NoteType)
class UserModel(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")