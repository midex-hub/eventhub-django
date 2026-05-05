from django.contrib import admin
from .models import TicketType


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'price', 'is_early_bird', 'quantity_available', 'quantity_sold']
    list_filter = ['is_early_bird', 'event']
    search_fields = ['name', 'event__title']
    readonly_fields = ['quantity_sold']
