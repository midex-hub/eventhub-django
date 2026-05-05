from django.db import models
from events.models import Event


class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)  # VIP, General, Early Bird
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_total = models.PositiveIntegerField()
    quantity_sold = models.PositiveIntegerField(default=0)
    is_early_bird = models.BooleanField(default=False)
    early_bird_deadline = models.DateTimeField(null=True, blank=True)
    sale_start = models.DateTimeField(null=True, blank=True)
    sale_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.event.title} - {self.name}"

    @property
    def quantity_available(self):
        return self.quantity_total - self.quantity_sold

    @property
    def is_sold_out(self):
        return self.quantity_available <= 0

    @property
    def availability_percentage(self):
        if self.quantity_total == 0:
            return 0
        return int((self.quantity_available / self.quantity_total) * 100)
