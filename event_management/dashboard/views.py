from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum
from django.urls import reverse_lazy
from accounts.models import CustomUser
from accounts.decorators import role_required
from events.models import Event, Category
from bookings.models import Booking, CheckIn
from tickets.models import TicketType
from .forms import *


@login_required
def attendee_dashboard(request):
    bookings = Booking.objects.filter(user=request.user).select_related('event').order_by('-created_at')
    return render(request, 'dashboard/attendee_dashboard.html', {'bookings': bookings})


@role_required('organizer')
def organizer_dashboard(request):
    events = Event.objects.filter(organizer=request.user)
    total_bookings = Booking.objects.filter(event__organizer=request.user, status='confirmed').count()
    total_revenue = sum(b.total_amount for b in Booking.objects.filter(event__organizer=request.user, status='confirmed'))
    return render(request, 'dashboard/organizer_dashboard.html', {
        'events': events,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
    })


@role_required('organizer')
def create_event(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        event = Event.objects.create(
            organizer=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            short_description=request.POST.get('short_description', ''),
            location=request.POST['location'],
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            category_id=request.POST.get('category') or None,
            status=request.POST.get('status', 'draft'),
            max_attendees=request.POST.get('max_attendees') or None,
            schedule=request.POST.get('schedule', ''),
        )
        if 'poster' in request.FILES:
            event.poster = request.FILES['poster']
            event.save()
        # Create ticket types
        names = request.POST.getlist('ticket_name[]')
        prices = request.POST.getlist('ticket_price[]')
        quantities = request.POST.getlist('ticket_quantity[]')
        for n, p, q in zip(names, prices, quantities):
            if n and p and q:
                TicketType.objects.create(event=event, name=n, price=p, quantity_total=q)
        messages.success(request, f'Event "{event.title}" created successfully!')
        if request.user.is_admin:
            return redirect('admin_event_list')
        return redirect('organizer_dashboard')
    return render(request, 'dashboard/create_event.html', {'categories': categories})


@role_required('organizer')
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    categories = Category.objects.all()
    if request.method == 'POST':
        event.title = request.POST['title']
        event.description = request.POST['description']
        event.short_description = request.POST.get('short_description', '')
        event.location = request.POST['location']
        event.start_date = request.POST['start_date']
        event.end_date = request.POST['end_date']
        event.category_id = request.POST.get('category') or None
        event.status = request.POST.get('status', 'draft')
        if 'poster' in request.FILES:
            event.poster = request.FILES['poster']
        event.save()
        messages.success(request, 'Event updated successfully!')
        return redirect('organizer_dashboard')
    return render(request, 'dashboard/edit_event.html', {'event': event, 'categories': categories})


@role_required('organizer')
def event_attendees(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    bookings = Booking.objects.filter(event=event, status='confirmed').select_related('user')
    return render(request, 'dashboard/event_attendees.html', {'event': event, 'bookings': bookings})


@role_required('organizer')
def checkin_view(request):
    events = Event.objects.filter(organizer=request.user, status='published')
    if request.method == 'POST':
        code = request.POST.get('qr_code', '')
        from bookings.models import QRCode
        try:
            qr = QRCode.objects.get(code=code)
            if qr.is_used:
                return render(request, 'dashboard/checkin.html', {'events': events, 'result': 'already_used', 'qr': qr})
            from django.utils import timezone
            qr.is_used = True
            qr.used_at = timezone.now()
            qr.save()
            CheckIn.objects.create(qr_code=qr, checked_in_by=request.user)
            return render(request, 'dashboard/checkin.html', {'events': events, 'result': 'success', 'qr': qr})
        except QRCode.DoesNotExist:
            return render(request, 'dashboard/checkin.html', {'events': events, 'result': 'invalid'})
    return render(request, 'dashboard/checkin.html', {'events': events})


@role_required('admin')
def admin_dashboard(request):
    from payments.models import Payment, WithdrawalRequest
    
    total_users = CustomUser.objects.count()
    users = CustomUser.objects.all()
    users_by_role = CustomUser.objects.values('role').annotate(count=Count('role'))
    
    total_events = Event.objects.count()
    events = Event.objects.all()
    all_events = events.select_related('organizer', 'category')[:20]
    
    total_bookings = Booking.objects.count()
    bookings = Booking.objects.all()
    recent_bookings = bookings.select_related('user', 'event').order_by('-created_at')[:5]
    
    payments = Payment.objects.filter(status='completed')
    total_revenue = sum(p.amount for p in payments)
    
    total_categories = Category.objects.count()

    # Withdrawal Requests
    withdrawal_requests = WithdrawalRequest.objects.all().order_by('-created_at')
    pending_withdrawals = withdrawal_requests.filter(status='pending')
    total_commission = WithdrawalRequest.objects.filter(status='completed').aggregate(total=Sum('admin_commission'))['total'] or 0
    
    return render(request, 'dashboard/admin_dashboard.html', {
        'total_users': total_users,
        'users': users,
        'users_by_role': users_by_role,
        'total_events': total_events,
        'all_events': all_events,
        'events': events,
        'total_bookings': total_bookings,
        'bookings': bookings,
        'recent_bookings': recent_bookings,
        'total_revenue': total_revenue,
        'total_categories': total_categories,
        'withdrawal_requests': withdrawal_requests[:10],
        'pending_withdrawals_count': pending_withdrawals.count(),
        'total_commission': total_commission,
    })


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin

    def handle_no_permission(self):
        messages.error(self.request, 'Admin access required.')
        return redirect('home')


class OrganizerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_organizer or self.request.user.is_admin

    def handle_no_permission(self):
        messages.error(self.request, 'Organizer access required.')
        return redirect('home')


# Admin CRUD for Category (example - simple model)
class CategoryListView(AdminRequiredMixin, ListView):
    model = Category
    template_name = 'dashboard/admin/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20


class CategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'dashboard/admin/category_form.html'
    success_url = reverse_lazy('admin_category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)


class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'dashboard/admin/category_form.html'
    success_url = reverse_lazy('admin_category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)


class CategoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'dashboard/admin/category_confirm_delete.html'
    success_url = reverse_lazy('admin_category_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Category deleted successfully!')
        return super(CategoryDeleteView, self).delete(request, *args, **kwargs)


# Admin CRUD for Users
class UserListView(AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'dashboard/admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserForm
    template_name = 'dashboard/admin/user_form.html'
    success_url = reverse_lazy('admin_user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully!')
        return super().form_valid(form)


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'dashboard/admin/user_confirm_delete.html'
    success_url = reverse_lazy('admin_user_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Admin CRUD for Events
class EventAdminListView(AdminRequiredMixin, ListView):
    model = Event
    template_name = 'dashboard/admin/event_list.html'
    context_object_name = 'events'
    paginate_by = 20


class EventAdminUpdateView(AdminRequiredMixin, UpdateView):
    model = Event
    form_class = AdminEventForm
    template_name = 'dashboard/admin/event_form.html'
    success_url = reverse_lazy('admin_event_list')

    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)


class EventAdminDeleteView(AdminRequiredMixin, DeleteView):
    model = Event
    template_name = 'dashboard/admin/event_confirm_delete.html'
    success_url = reverse_lazy('admin_event_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Event deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Admin CRUD for Bookings
class BookingAdminListView(AdminRequiredMixin, ListView):
    model = Booking
    template_name = 'dashboard/admin/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        return super().get_queryset().select_related('user', 'event')


class BookingAdminUpdateView(AdminRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'dashboard/admin/booking_form.html'
    success_url = reverse_lazy('admin_booking_list')

    def form_valid(self, form):
        messages.success(self.request, 'Booking updated successfully!')
        return super().form_valid(form)


class BookingAdminDeleteView(AdminRequiredMixin, DeleteView):
    model = Booking
    template_name = 'dashboard/admin/booking_confirm_delete.html'
    success_url = reverse_lazy('admin_booking_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Booking deleted successfully!')
        return super().delete(request, *args, **kwargs)
