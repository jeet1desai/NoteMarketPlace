from django.urls import path
from . import views

urlpatterns = [
    path('contact_us/', views.ContactUs.as_view(), name="contact us"),

    path('category_list/', views.NoteCategoryList.as_view(), name="user category list"),
    path('type_list/', views.NoteTypeList.as_view(), name="user type list"),
    path('country_list/', views.CountryList.as_view(), name="user country list"),

    path('profile/<int:user_id>/', views.ProfileDetails.as_view(), name="get profile"),
    
    # seller, buyer, update profile
]
