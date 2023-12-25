from django.urls import path
from . import views

urlpatterns = [
    # config
    path('config_get/', views.GetConfiguration.as_view(), name="config get"),
    path('config_post/', views.PostConfiguration.as_view(), name="config post"),
    # admin
    path('admins/', views.Admin.as_view(), name="admins get"),
    path('admin/<int:admin_id>/', views.Admin.as_view(), name="admin get"),
    path('admin_post/', views.Admin.as_view(), name="admin post"),
    path('admin_put/<int:admin_id>/', views.Admin.as_view(), name="admin update"),
    path('admin_delete/<int:admin_id>/', views.Admin.as_view(), name="admin delete"),
    # country
    path('countries/', views.Countries.as_view(), name="countries get"),
    path('country/<int:country_id>/', views.Countries.as_view(), name="country get"),
    path('country_post/', views.Countries.as_view(), name="country post"),
    path('country_put/<int:country_id>/', views.Countries.as_view(), name="country update"),
    path('country_delete/<int:country_id>/', views.Countries.as_view(), name="country delete"),
    # note category
    path('categories/', views.NoteCategories.as_view(), name="categories get"),
    path('category/<int:category_id>/', views.NoteCategories.as_view(), name="category get"),
    path('category_post/', views.NoteCategories.as_view(), name="category post"),
    path('category_put/<int:category_id>/', views.NoteCategories.as_view(), name="category update"),
    path('category_delete/<int:category_id>/', views.NoteCategories.as_view(), name="category delete"),
    # note type
    path('types/', views.NoteTypes.as_view(), name="types get"),
    path('type/<int:type_id>/', views.NoteTypes.as_view(), name="type get"),
    path('type_post/', views.NoteTypes.as_view(), name="type post"),
    path('type_put/<int:type_id>/', views.NoteTypes.as_view(), name="type update"),
    path('type_delete/<int:type_id>/', views.NoteTypes.as_view(), name="type delete"),
]
