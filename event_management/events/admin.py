from django.contrib import admin
from .models import Event, Category, Speaker

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'category', 'start_date', 'status', 'is_featured')
    list_filter = ('status', 'category', 'is_featured')
    search_fields = ('title', 'location')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'icon']
    list_filter = ['color']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'title']
    list_filter = ['event']
    search_fields = ['name', 'title']
