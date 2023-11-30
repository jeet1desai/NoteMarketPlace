from django.urls import path
from . import views

urlpatterns = [
    # config
    path('create_note/', views.Note.as_view(), name="create Note"),
]
