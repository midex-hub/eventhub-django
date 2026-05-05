from django import forms
from django.forms import ModelChoiceField, ModelMultipleChoiceField
from accounts.models import CustomUser
from events.models import Category, Event, Speaker
from tickets.models import TicketType
from bookings.models import Booking, BookingItem, QRCode, CheckIn
from payments.models import Payment


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'phone', 'avatar', 'bio', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'role': forms.Select(choices=CustomUser.ROLE_CHOICES),
            'avatar': forms.ClearableFileInput(),
            'bio': forms.Textarea(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select bg-dark text-white border-secondary'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input bg-dark border-secondary'})
            else:
                field.widget.attrs.update({'class': 'form-control bg-dark text-white border-secondary'})


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'icon': forms.TextInput(attrs={'placeholder': 'bi-calendar-event'}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'short_description', 'poster', 'location', 'latitude', 'longitude', 'start_date', 'end_date', 'category', 'status', 'is_featured', 'max_attendees', 'schedule']
        widgets = {
            'title': forms.TextInput(attrs={'required': True}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'short_description': forms.TextInput(),
            'poster': forms.ClearableFileInput(),
            'location': forms.TextInput(attrs={'required': True}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'status': forms.Select(choices=Event.STATUS_CHOICES),
            'schedule': forms.Textarea(attrs={'rows': 3}),
        }


class AdminEventForm(EventForm):
    class Meta(EventForm.Meta):
        fields = ['organizer'] + EventForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select bg-dark text-white border-secondary'})
            elif isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs.update({'class': 'form-check-input bg-dark border-secondary'})
            else:
                field.widget.attrs.update({'class': 'form-control bg-dark text-white border-secondary'})


class SpeakerForm(forms.ModelForm):
    class Meta:
        model = Speaker
        fields = '__all__'
        widgets = {
            'photo': forms.ClearableFileInput(),
            'bio': forms.Textarea(),
        }


class TicketTypeForm(forms.ModelForm):
    class Meta:
        model = TicketType
        fields = '__all__'
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'quantity_total': forms.NumberInput(),
            'early_bird_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sale_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sale_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['event', 'status', 'guest_name', 'guest_email', 'guest_phone']
        widgets = {
            'status': forms.Select(choices=Booking.STATUS_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select bg-dark text-white border-secondary'})
            else:
                field.widget.attrs.update({'class': 'form-control bg-dark text-white border-secondary'})


class BookingItemForm(forms.ModelForm):
    class Meta:
        model = BookingItem
        fields = '__all__'
        widgets = {
            'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
        }


class QRCodeForm(forms.ModelForm):
    class Meta:
        model = QRCode
        fields = ['is_used']  # Mostly readonly, manual toggle


class CheckInForm(forms.ModelForm):
    class Meta:
        model = CheckIn
        fields = []  # Mostly auto


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['status', 'method', 'transaction_id']
        widgets = {
            'status': forms.Select(choices=Payment.STATUS_CHOICES),
            'method': forms.Select(choices=Payment.METHOD_CHOICES),
        }
