from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'short_description',
            'category', 'venue_name', 'address', 'city',
            'state', 'country', 'latitude', 'longitude',
            'start_date', 'end_date', 'poster', 'banner',
            'status', 'is_featured', 'max_attendees',
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 6}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
        }
