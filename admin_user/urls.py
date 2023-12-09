from django.urls import path
from . import views

urlpatterns = [
    path('note_under_review', views.NoteUnderReview.as_view(), name="note under review"),
    path('published_note/', views.PublishedNotes.as_view(), name="published note"),
    path('downloaded_note/', views.DownloadedNotes.as_view(), name="downloaded note"),
    path('rejected_note/', views.RejectedNotes.as_view(), name="rejected note"),

    path('update_status/', views.NoteUpdateStatus.as_view(), name="update status"),
    path('update_remark_status/', views.NoteUpdateRemarkStatus.as_view(), name="update status; remark"),

    path('members/', views.Members.as_view(), name="members"),
    path('members/<int:user_id>/', views.Members.as_view(), name="deactivate members"),

    path('user_notes/<int:user_id>/', views.AllUserNotes.as_view(), name="all user notes"),

    # stats, report span and span list
]
