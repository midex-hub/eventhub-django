from django.contrib import admin
from .models import Booking, BookingItem, QRCode, CheckIn


class BookingItemInline(admin.TabularInline):
    model = BookingItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'guest_name', 'guest_email', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'guest_email', 'guest_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'guest_name', 'guest_email']
    inlines = [BookingItemInline]


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['booking_item', 'code', 'used_at']
    readonly_fields = ['used_at']


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ['qr_code', 'checked_in_by', 'checked_in_at']
    readonly_fields = ['checked_in_at']
