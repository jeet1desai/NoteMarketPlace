from django.urls import path
from . import views

urlpatterns = [
    path('create_note/<int:uStatus>/', views.Note.as_view(), name="create note"),
    path('update_note/<int:note_id>/<int:uStatus>/', views.Note.as_view(), name="update note"),

    path('in_progress_note', views.InProgressNote.as_view(), name="in progress note"),
    path('published_note', views.PublishedNote.as_view(), name="published note"),
    
    path('rejected_note', views.RejectedNote.as_view(), name="rejected note"),
    path('clone_note/', views.CloneNoteView.as_view(), name="clone note"),

    path('download_note/', views.DownloadNote.as_view(), name="download note"),
    
    # note detail (with review), user note (except draft), note list (with all search and filter)
    # stats, buyer request (allow download), my download list
    # add review, my sold note, 
]
