from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    # path('admin/', admin.site.urls),  # Disabled - using custom dashboard
    path('', include('events.urls')),
    path('', include('accounts.urls')),
    path('', include('bookings.urls')),
    path('', include('payments.urls')),
    path('dashboard/', include('dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
