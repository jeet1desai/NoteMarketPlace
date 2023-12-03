from django.urls import path
from . import views

urlpatterns = [
    path('note_under_review', views.NoteUnderReview.as_view(), name="note under review"),
    # in progress
    path('published_note', views.PublishedNotes.as_view(), name="published note"),

    path('update_status/', views.NoteUpdateStatus.as_view(), name="update status"),
    path('update_remark_status/', views.NoteUpdateRemarkStatus.as_view(), name="update status; remark"),

    # member, delete review, stats, 2 published note, all download notes, all rejected note
    # deactivate member
]
