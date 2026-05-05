import requests
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from accounts.decorators import role_required
from bookings.models import Booking
from .models import Payment, WithdrawalRequest
from .forms import WithdrawalRequestForm
from django.db.models import Sum
from decimal import Decimal

logger = logging.getLogger(__name__)


@login_required
def request_withdrawal(request):
    if not request.user.is_organizer:
        messages.error(request, "Only organizers can request withdrawals.")
        return redirect('home')
    
    if request.method == 'POST':
        form = WithdrawalRequestForm(request.POST, user=request.user)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.user = request.user
            
            # Calculate Commission (10%) and Payout (90%)
            amount = withdrawal.amount_requested
            withdrawal.admin_commission = amount * Decimal('0.10')
            withdrawal.payout_amount = amount * Decimal('0.90')
            
            withdrawal.save()
            messages.success(request, f"Withdrawal request for ₦{amount} submitted successfully. It will be processed soon.")
            return redirect('organizer_dashboard')
    else:
        form = WithdrawalRequestForm(user=request.user)
    
    return render(request, 'payments/request_withdrawal.html', {
        'form': form,
        'released_balance': request.user.released_balance,
        'pending_balance': request.user.pending_balance,
    })


def payment_process(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payment, _ = Payment.objects.get_or_create(booking=booking, defaults={'amount': booking.total_amount})

    if request.method == 'POST':
        # Initialize Paystack payment
        paystack_public_key = settings.PAYSTACK_PUBLIC_KEY
        paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        paystack_base_url = settings.PAYSTACK_BASE_URL
        
        # Prepare payment initialization request
        callback_url = request.build_absolute_uri('/callback/')
        data = {
            'amount': int(payment.amount * 100),  # Paystack expects amount in kobo
            'email': booking.user.email,
            'reference': f"EVT_{booking.reference}_{payment.id}",
            'callback_url': callback_url,
            'metadata': {
                'booking_id': booking.id,
                'payment_id': payment.id,
            }
        }
        
        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
            'Content-Type': 'application/json',
        }
        
        try:
            logger.info(f"Initializing Paystack payment for booking {booking.id}, reference: {data['reference']}")
            response = requests.post(
                f'{paystack_base_url}/transaction/initialize',
                json=data,
                headers=headers,
                timeout=30
            )
            result = response.json()
            
            if result.get('status') == True:
                # Save the Paystack reference
                payment.paystack_reference = result['data']['reference']
                payment.save()
                # Redirect to Paystack payment page
                return redirect(result['data']['authorization_url'])
            else:
                messages.error(request, f"Payment initialization failed: {result.get('message', 'Unknown error')}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Paystack timeout for booking {booking.id}: {str(e)}")
            messages.error(request, "Payment service timeout. Please check your internet connection and try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack request error for booking {booking.id}: {str(e)}")
            messages.error(request, "Payment service unavailable. Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected payment error for booking {booking.id}: {str(e)}")
            messages.error(request, f"Payment error: {str(e)}")
        
        # Fallback: Simulate payment success ONLY in DEBUG mode
        if settings.DEBUG:
            logger.warning(f"Using DEBUG fallback for booking {booking.id}")
            payment.status = 'completed'
            payment.transaction_id = f"sim_{booking.reference}"
            payment.save()
            
            # Credit the organizer's balance
            organizer = booking.event.organizer
            organizer.balance += payment.amount
            organizer.save()
            
            booking.status = 'confirmed'
            booking.save()
            
            # Update ticket quantity_sold for each booking item
            for item in booking.items.all():
                ticket_type = item.ticket_type
                ticket_type.quantity_sold += item.quantity
                ticket_type.save()
            
            # Generate QR codes
            for item in booking.items.all():
                from bookings.models import QRCode
                QRCode.objects.get_or_create(booking_item=item)
            
            # Redirect to ticket detail for logged-in users, otherwise to booking success
            first_item = booking.items.first()
            if request.user.is_authenticated and first_item:
                return redirect('ticket_detail', booking_id=booking.id, item_id=first_item.id)
            return redirect('booking_success', booking_id=booking.id)
        else:
            return render(request, 'payments/payment.html', {
                'booking': booking,
                'payment': payment,
                'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
                'error': 'Payment initialization failed. Please try again.',
            })

    return render(request, 'payments/payment.html', {
        'booking': booking,
        'payment': payment,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
    })


def payment_callback(request):
    """Handle Paystack payment callback"""
    reference = request.GET.get('reference')
    
    if reference:
        paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        paystack_base_url = settings.PAYSTACK_BASE_URL
        
        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
        }
        
        try:
            logger.info(f"Verifying Paystack payment: {reference}")
            response = requests.get(
                f'{paystack_base_url}/transaction/verify/{reference}',
                headers=headers,
                timeout=30
            )
            result = response.json()
            
            if result.get('status') == True and result['data']['status'] == 'success':
                # Find payment by reference
                payment = Payment.objects.filter(paystack_reference=reference).first()
                if payment:
                    payment.status = 'completed'
                    payment.transaction_id = reference
                    payment.paystack_authorization_code = result['data']['authorization']['authorization_code']
                    payment.save()
                    
                    # Credit the organizer's balance
                    booking = payment.booking
                    organizer = booking.event.organizer
                    organizer.balance += payment.amount
                    organizer.save()
                    
                    # Update booking status
                    booking.status = 'confirmed'
                    booking.save()
                    
                    # Update ticket quantity_sold for each booking item
                    for item in booking.items.all():
                        ticket_type = item.ticket_type
                        ticket_type.quantity_sold += item.quantity
                        ticket_type.save()
                    
                    # Generate QR codes
                    for item in booking.items.all():
                        from bookings.models import QRCode
                        QRCode.objects.get_or_create(booking_item=item)
                    
                    # Redirect to ticket detail for logged-in users, otherwise to booking success
                    first_item = booking.items.first()
                    if booking.user and first_item:
                        return redirect('ticket_detail', booking_id=booking.id, item_id=first_item.id)
                    return redirect('booking_success', booking_id=booking.id)
        except requests.exceptions.Timeout as e:
            logger.error(f"Paystack verify timeout for reference {reference}: {str(e)}")
            messages.error(request, "Payment verification timeout.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack verify request error for {reference}: {str(e)}")
            messages.error(request, "Payment verification failed. Please contact support.")
        except Exception as e:
            logger.error(f"Unexpected verify error for {reference}: {str(e)}")
            messages.error(request, f"Payment verification error: {str(e)}")
    
    messages.error(request, "Payment verification failed")
    # Get the booking from the payment if available, otherwise redirect to home
    if reference:
        payment = Payment.objects.filter(paystack_reference=reference).first()
        if payment:
            return redirect('payment_process', booking_id=payment.booking.id)
    return redirect('home')


@role_required('admin')
def admin_withdrawal_list(request):
    withdrawals = WithdrawalRequest.objects.all().order_by('-created_at')
    return render(request, 'payments/admin_withdrawal_list.html', {
        'withdrawals': withdrawals
    })


@role_required('admin')
def complete_withdrawal(request, withdrawal_id):
    withdrawal = get_object_or_404(WithdrawalRequest, id=withdrawal_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_note = request.POST.get('admin_note', '')
        
        if action == 'complete':
            withdrawal.status = 'completed'
            withdrawal.admin_note = admin_note
            withdrawal.save()
            messages.success(request, f"Withdrawal for {withdrawal.user.username} marked as completed.")
        elif action == 'reject':
            withdrawal.status = 'rejected'
            withdrawal.admin_note = admin_note
            withdrawal.save()
            messages.warning(request, f"Withdrawal for {withdrawal.user.username} rejected.")
            
    return redirect('admin_withdrawal_list')
