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
    list_display = ['booking_item', 'code', 'is_used', 'used_at']
    readonly_fields = ['used_at']
    actions = ['regenerate_qr_codes']

    @admin.action(description='Regenerate selected QR codes')
    def regenerate_qr_codes(self, request, queryset):
        for qr in queryset:
            qr.regenerate_image()
        self.message_user(request, f"Successfully regenerated {queryset.count()} QR codes.")


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ['qr_code', 'checked_in_by', 'checked_in_at']
    readonly_fields = ['checked_in_at']
