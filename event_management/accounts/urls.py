from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('email-verification-sent/', TemplateView.as_view(template_name='accounts/email_verification_sent.html'), name='email_verification_sent'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('password-reset/', views.password_reset_request_view, name='password_reset'),
    path('password-reset/verify/', views.password_reset_verify_view, name='password_reset_verify'),
    path('password-reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('admin-setup/<uuid:token>/', views.admin_setup_view, name='admin_setup'),
]
