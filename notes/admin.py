from django.contrib import admin
from .models import SellerNotes, Downloads, SellerNotesReviews, SellerNotesReportedIssues

# Register your models here.
@admin.register(SellerNotes)
class UserModel(admin.ModelAdmin):
    list_filter = ("title", "status", "is_active")
    list_display = ("id", "title", "status", "is_paid", "selling_price", "modified_by", "is_active")

@admin.register(Downloads)
class UserModel(admin.ModelAdmin):
    list_display = ("id", "note", "seller", "downloader")

@admin.register(SellerNotesReviews)
class UserModel(admin.ModelAdmin):
    list_display = ("id", "note", "rating", "is_active")

@admin.register(SellerNotesReportedIssues)
class SellerNotesReportedIssuesModel(admin.ModelAdmin):
    list_display = ("id", "remarks", "note", "reported_by", "is_active")
