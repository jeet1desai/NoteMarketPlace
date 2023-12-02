from django.urls import path
from . import views

urlpatterns = [
    path('contact_us/', views.ContactUs.as_view(), name="contact us"),
]
