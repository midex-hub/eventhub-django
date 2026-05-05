from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
]
