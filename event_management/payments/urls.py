from django.urls import path
from . import views

urlpatterns = [
    path('payment/<int:booking_id>/', views.payment_process, name='payment_process'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('withdraw/', views.request_withdrawal, name='request_withdrawal'),
    path('admin/withdrawals/', views.admin_withdrawal_list, name='admin_withdrawal_list'),
    path('admin/withdrawals/<int:withdrawal_id>/complete/', views.complete_withdrawal, name='complete_withdrawal'),
]
