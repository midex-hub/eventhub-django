import uuid
import qrcode
import io
from django.db import models
from django.core.files.base import ContentFile
from django.conf import settings
from django.urls import reverse
from accounts.models import CustomUser
from events.models import Event
from tickets.models import TicketType


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    reference = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    guest_name = models.CharField(max_length=100, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.reference} - {self.event.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"EVT{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class BookingItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    attendee_name = models.CharField(max_length=100, blank=True)
    attendee_email = models.EmailField(blank=True)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.booking.reference} - {self.ticket_type.name} x{self.quantity}"


class QRCode(models.Model):
    booking_item = models.OneToOneField(BookingItem, on_delete=models.CASCADE, related_name='qr_code')
    code = models.CharField(max_length=100, unique=True, blank=True)
    image = models.ImageField(upload_to='qrcodes/', blank=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"QR{uuid.uuid4().hex[:8].upper()}"
        if not self.image:
            self._generate_qr_image()
        super().save(*args, **kwargs)

    def _generate_qr_image(self):
        # Build full URL so scanning the QR opens the ticket page directly
        site_url = settings.SITE_URL.rstrip('/')
        ticket_path = reverse('ticket_public', kwargs={'code': self.code})
        ticket_url = f"{site_url}{ticket_path}"

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(ticket_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        # If there's an existing image, we might want to delete it or overwrite it
        # self.image.save will handle the saving to storage
        filename = f'{self.code}.png'
        self.image.save(filename, ContentFile(buffer.getvalue()), save=False)

    def regenerate_image(self):
        """Force regeneration of the QR code image, useful if SITE_URL changes"""
        self._generate_qr_image()
        self.save()


class CheckIn(models.Model):
    qr_code = models.OneToOneField(QRCode, on_delete=models.CASCADE)
    checked_in_at = models.DateTimeField(auto_now_add=True)
    checked_in_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"CheckIn: {self.qr_code.code}"
