from django.urls import path
from . import views

urlpatterns = [
    path('contact_us/', views.ContactUs.as_view(), name="contact us"),

    path('category_list/', views.NoteCategoryList.as_view(), name="user category list"),
    path('type_list/', views.NoteTypeList.as_view(), name="user type list"),
    path('country_list/', views.CountryList.as_view(), name="user country list"),

    path('profile/<int:user_id>/', views.ProfileDetails.as_view(), name="get profile"),
    path('update_user/', views.UserProfileUpdate.as_view(), name="update user"),
    path('update_admin/', views.AdminProfileUpdate.as_view(), name="update admin"),

    path('add_review/', views.Review.as_view(), name="add review"),
    path('get_review/<int:note_id>/', views.Review.as_view(), name="get review"),
    path('delete_review/<int:review_id>/', views.Review.as_view(), name="delete review"),
    
    # seller, buyer
]
