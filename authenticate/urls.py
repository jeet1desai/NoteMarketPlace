from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.Register.as_view(), name="register"),
    path('login/', views.Login.as_view(), name="login"),
    path('verify_email/<int:user_id>/', views.VerifyEmail.as_view(), name="verify email"),
    path('change_password/', views.ChangePassword.as_view(), name="change password"),
    path('reset_password/', views.ResetPassword.as_view(), name="reset password"),
]
