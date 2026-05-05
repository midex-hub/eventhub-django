from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('organizer', 'Organizer'),
        ('attendee', 'Attendee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendee')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    twitter_link = models.URLField(max_length=200, blank=True)
    instagram_link = models.URLField(max_length=200, blank=True)
    website_link = models.URLField(max_length=200, blank=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_organizer(self):
        return self.role == 'organizer'

    @property
    def is_attendee(self):
        return self.role == 'attendee'

    @property
    def released_balance(self):
        """Total balance from events starting in <= 24 hours or already passed."""
        from events.models import Event
        release_threshold = timezone.now() + timedelta(hours=24)
        released_events = Event.objects.filter(organizer=self, start_date__lte=release_threshold)
        
        from bookings.models import Booking
        released_bookings = Booking.objects.filter(event__in=released_events, status='confirmed')
        total_released = sum(b.total_amount for b in released_bookings)
        
        completed_withdrawals = self.withdrawals.filter(status='completed')
        total_withdrawn = sum(w.amount_requested for w in completed_withdrawals)
        
        return max(total_released - total_withdrawn, 0)

    @property
    def pending_balance(self):
        """Funds that are still locked because the event is > 24 hours away."""
        return max(self.balance - self.released_balance, 0)
