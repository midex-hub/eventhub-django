from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
from .models import Booking, BookingItem, QRCode
from events.models import Event
from tickets.models import TicketType
import json


def checkout_view(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    ticket_types = event.ticket_types.filter(quantity_sold__lt=models.F('quantity_total'))
    
    if request.method == 'POST':
        # Process booking
        items_data = {}
        for tt in ticket_types:
            qty = int(request.POST.get(f'qty_{tt.id}', 0))
            if qty > 0:
                items_data[tt.id] = {'qty': qty, 'price': tt.price}

        if not items_data:
            messages.error(request, 'Please select at least one ticket.')
            return render(request, 'bookings/checkout.html', {'event': event, 'ticket_types': ticket_types})

        booking = Booking.objects.create(
            user=request.user if request.user.is_authenticated else None,
            event=event,
            guest_name=request.POST.get('guest_name', ''),
            guest_email=request.POST.get('guest_email', ''),
            guest_phone=request.POST.get('guest_phone', ''),
        )
        total = 0
        for tt_id, data in items_data.items():
            tt = get_object_or_404(TicketType, id=tt_id)
            BookingItem.objects.create(
                booking=booking,
                ticket_type=tt,
                quantity=data['qty'],
                unit_price=data['price'],
            )
            total += data['qty'] * data['price']
        booking.total_amount = total
        booking.save()
        request.session['pending_booking_id'] = booking.id
        return redirect('payment_process', booking_id=booking.id)

    ticket_types = event.ticket_types.all()
    return render(request, 'bookings/checkout.html', {'event': event, 'ticket_types': ticket_types})


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'bookings/booking_success.html', {'booking': booking})


@login_required
def ticket_detail_view(request, booking_id, item_id):
    """Show a single ticket detail with QR code"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    item = get_object_or_404(BookingItem, id=item_id, booking=booking)
    return render(request, 'bookings/ticket_detail.html', {'booking': booking, 'item': item})


def ticket_public_view(request, code):
    """Public ticket view — no login required. Accessed via QR code scan."""
    qr = get_object_or_404(QRCode, code=code)
    item = qr.booking_item
    booking = item.booking
    return render(request, 'bookings/ticket_public.html', {
        'qr': qr,
        'item': item,
        'booking': booking,
    })


@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'bookings/user_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'confirmed':
        # Decrement quantity_sold for each booking item to release tickets
        for item in booking.items.all():
            ticket_type = item.ticket_type
            ticket_type.quantity_sold = max(0, ticket_type.quantity_sold - item.quantity)
            ticket_type.save()
        
        # Deduct from organizer balance
        organizer = booking.event.organizer
        organizer.balance = max(0, organizer.balance - booking.total_amount)
        organizer.save()
        
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully. Your refund will be processed by the organizer.')
    return redirect('attendee_dashboard')
