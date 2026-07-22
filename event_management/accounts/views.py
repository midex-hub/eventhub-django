import random
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import CustomUser
from .utils import send_verification_email, send_reset_code_email


def generate_code():
    return str(random.randint(100000, 999999))


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_email_verified = True
            user.save()
            login(request, user)
            messages.success(request, f'Welcome {user.first_name or user.username}!')
            return redirect('dashboard_redirect')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_email_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    email = request.GET.get('email', request.POST.get('email', ''))
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        email = request.POST.get('email', '').strip()
        try:
            user = CustomUser.objects.get(email=email, is_email_verified=False)
            if user.email_verification_token == code:
                user.is_email_verified = True
                user.email_verification_token = ''
                user.save(update_fields=['is_email_verified', 'email_verification_token'])
                login(request, user)
                messages.success(request, f'Welcome {user.first_name or user.username}! Email verified.')
                return redirect('dashboard_redirect')
            else:
                messages.error(request, 'Invalid verification code.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No unverified account found with that email.')
    return render(request, 'accounts/verify_email.html', {'email': email})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard_redirect')
        messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def resend_verification_view(request):
    if request.user.is_email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('dashboard_redirect')
    request.user.email_verification_token = generate_code()
    request.user.save(update_fields=['email_verification_token'])
    send_verification_email(request.user, request)
    messages.success(request, 'New verification code sent. Please check your inbox.')
    return redirect('email_verification_sent')


def password_reset_request_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = CustomUser.objects.get(email=email)
            user.reset_code = generate_code()
            user.reset_code_created_at = timezone.now()
            user.save(update_fields=['reset_code', 'reset_code_created_at'])
            send_reset_code_email(user, request)
            messages.success(request, 'Password reset code sent to your email.')
            return redirect('password_reset_verify')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with that email.')
    return render(request, 'accounts/password_reset.html')


def password_reset_verify_view(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        email = request.POST.get('email', '').strip()
        try:
            user = CustomUser.objects.get(email=email)
            if user.reset_code != code:
                messages.error(request, 'Invalid reset code.')
                return render(request, 'accounts/password_reset_verify.html', {'email': email})
            if not user.reset_code_created_at or timezone.now() - user.reset_code_created_at > timedelta(minutes=15):
                messages.error(request, 'Reset code has expired. Request a new one.')
                return redirect('password_reset')
            request.session['reset_user_id'] = user.id
            return redirect('password_reset_confirm')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with that email.')
            return redirect('password_reset')
    return render(request, 'accounts/password_reset_verify.html')


def password_reset_confirm_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Start over.')
        return redirect('password_reset')
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('password_reset')
    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm', '')
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif password != confirm:
            messages.error(request, 'Passwords do not match.')
        else:
            user.set_password(password)
            user.reset_code = ''
            user.reset_code_created_at = None
            user.save(update_fields=['password', 'reset_code', 'reset_code_created_at'])
            del request.session['reset_user_id']
            messages.success(request, 'Password reset successful. Login with your new password.')
            return redirect('login')
    return render(request, 'accounts/password_reset_confirm.html')


@login_required
def dashboard_redirect(request):
    user = request.user
    if user.is_admin:
        return redirect('admin_dashboard')
    elif user.is_organizer:
        return redirect('organizer_dashboard')
    return redirect('attendee_dashboard')


def admin_setup_view(request, token):
    if CustomUser.objects.filter(is_superuser=True).exists():
        messages.error(request, 'Admin account already exists. This link is no longer valid.')
        return redirect('login')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        if not all([username, email, password]):
            messages.error(request, 'All fields are required.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            user = CustomUser.objects.create_superuser(
                username=username, email=email, password=password
            )
            user.role = 'admin'
            user.is_email_verified = True
            user.save(update_fields=['role', 'is_email_verified'])
            login(request, user)
            messages.success(request, 'Admin account created! Welcome.')
            return redirect('dashboard_redirect')
    return render(request, 'accounts/admin_setup.html')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})
