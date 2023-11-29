from django.contrib import admin
from .models import User

# Register your models here.
# admin.site.register(User)
@admin.register(User)
class UserModel(admin.ModelAdmin):
    list_filter = ("role_id", "email", "is_active")
    list_display = ("id", "first_name", "last_name", "email", "role_id", "is_email_verified", "is_active")