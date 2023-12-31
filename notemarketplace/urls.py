from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include("authenticate.urls")),
    path('api/v1/super_admin/', include("super_admin.urls")),
    path('api/v1/note/', include("notes.urls")),
    path('api/v1/user/', include("user.urls")),
    path('api/v1/admin/', include("admin_user.urls")),
]
