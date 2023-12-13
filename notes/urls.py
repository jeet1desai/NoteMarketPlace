from django.urls import path
from . import views

urlpatterns = [
    path('create_note/<int:uStatus>/', views.Note.as_view(), name="create note"),
    path('update_note/<int:note_id>/<int:uStatus>/', views.Note.as_view(), name="update note"),

    path('in_progress_note/', views.InProgressNote.as_view(), name="in progress note"),
    path('published_note/', views.PublishedNote.as_view(), name="published note"),
    
    path('rejected_note', views.RejectedNote.as_view(), name="rejected note"),
    path('clone_note/', views.CloneNoteView.as_view(), name="clone note"),

    path('download_note/', views.DownloadNote.as_view(), name="download note"),

    path('buyer_request/', views.BuyerRequests.as_view(), name="buyer request"),
    path('buyer_request/', views.BuyerRequests.as_view(), name="buyer request update"),

    path('my_sold_note/', views.MySoldNotes.as_view(), name="my sold note"),
    path('my_download_note/', views.MyDownloadNotes.as_view(), name="my download note"),

    path('get_note/<int:note_id>/', views.NoteDetails.as_view(), name="get notes"),

    # stats, note list (with all search and filter)
]
