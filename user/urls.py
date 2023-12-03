from django.urls import path
from . import views

urlpatterns = [
    # seller, buyer, category, type, country, profile, update profile
    path('contact_us/', views.ContactUs.as_view(), name="contact us"),
]
