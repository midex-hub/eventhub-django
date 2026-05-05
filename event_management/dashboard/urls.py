from django.urls import path
from . import views

urlpatterns = [
    path('attendee/', views.attendee_dashboard, name='attendee_dashboard'),
    path('organizer/', views.organizer_dashboard, name='organizer_dashboard'),
    path('organizer/events/create/', views.create_event, name='create_event'),
    path('organizer/events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('organizer/events/<int:event_id>/attendees/', views.event_attendees, name='event_attendees'),
    path('organizer/checkin/', views.checkin_view, name='checkin'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    # Admin CRUD
    path('admin/categories/', views.CategoryListView.as_view(), name='admin_category_list'),
    path('admin/categories/create/', views.CategoryCreateView.as_view(), name='admin_category_create'),
    path('admin/categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='admin_category_update'),
    path('admin/categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='admin_category_delete'),
    
    # Admin Users
    path('admin/users/', views.UserListView.as_view(), name='admin_user_list'),
    path('admin/users/<int:pk>/update/', views.UserUpdateView.as_view(), name='admin_user_update'),
    path('admin/users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='admin_user_delete'),
    
    # Admin Events
    path('admin/events/', views.EventAdminListView.as_view(), name='admin_event_list'),
    path('admin/events/<int:pk>/update/', views.EventAdminUpdateView.as_view(), name='admin_event_update'),
    path('admin/events/<int:pk>/delete/', views.EventAdminDeleteView.as_view(), name='admin_event_delete'),
    
    # Admin Bookings
    path('admin/bookings/', views.BookingAdminListView.as_view(), name='admin_booking_list'),
    path('admin/bookings/<int:pk>/update/', views.BookingAdminUpdateView.as_view(), name='admin_booking_update'),
    path('admin/bookings/<int:pk>/delete/', views.BookingAdminDeleteView.as_view(), name='admin_booking_delete'),
]
