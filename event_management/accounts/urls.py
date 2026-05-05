from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    path('verify-email/<str:token>/', views.verify_email_view, name='verify_email'),
    path('email-verification-sent/', TemplateView.as_view(template_name='accounts/email_verification_sent.html'), name='email_verification_sent'),
    path('profile/', views.profile_view, name='profile'),
    path('create-secret-admin/', views.create_admin_temp_view, name='create_secret_admin'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]
