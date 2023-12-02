from django.urls import path
from . import views

urlpatterns = [
    # user note
    path('create_note/<int:status>/', views.Note.as_view(), name="create Note"),
    path('update_note/<int:note_id>/<int:status>/', views.Note.as_view(), name="update Note"),
    path('in_progress_note', views.InProgressNote.as_view(), name="in progress note Note"),
    path('published_note', views.PublishedNote.as_view(), name="published Note"),
    path('rejected_note', views.RejectedNote.as_view(), name="rejected Note"),
    path('clone_note/', views.CloneNoteView.as_view(), name="clone Note"),
]
