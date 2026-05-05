from django.urls import path
from . import views

urlpatterns = [
    path('events/<slug:slug>/checkout/', views.checkout_view, name='checkout'),
    path('booking/<int:booking_id>/success/', views.booking_success, name='booking_success'),
    path('booking/<int:booking_id>/ticket/<int:item_id>/', views.ticket_detail_view, name='ticket_detail'),
    path('ticket/qr/<str:code>/', views.ticket_public_view, name='ticket_public'),
    path('my-bookings/', views.user_bookings, name='user_bookings'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
]
