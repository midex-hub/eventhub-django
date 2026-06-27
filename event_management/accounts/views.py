import os
from django.shortcuts import render, redirect
import threading
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import CustomUser
from .utils import send_verification_email


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_email_verified = False
            user.save()
            
            send_verification_email(user, request)
            
            messages.success(request, 'Registration successful! Please check your email to verify your account before logging in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # TEMPORARILY DISABLED EMAIL VERIFICATION
            # if not user.is_email_verified:
            #     messages.error(request, 'Please verify your email address before logging in. Check your inbox for the verification link.')
            #     return redirect('login')
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
    """Resend verification email for logged-in unverified users."""
    if request.user.is_email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('dashboard_redirect')
    send_verification_email(request.user, request)
    messages.success(request, 'Verification email resent. Please check your inbox.')
    return redirect('email_verification_sent')


def verify_email_view(request, token):
    """Verify user email using token."""
    try:
        user = CustomUser.objects.get(
            email_verification_token=token,
            is_email_verified=False
        )
        if timezone.now() - user.created_at > timedelta(hours=24):
            messages.error(request, 'Verification link has expired. Please register again or contact support.')
            return redirect('register')
        user.is_email_verified = True
        user.email_verification_token = ''
        user.save(update_fields=['is_email_verified', 'email_verification_token'])
        login(request, user)
        messages.success(request, f'Welcome {user.first_name}! Your email has been verified.')
        return redirect('dashboard_redirect')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('login')


@login_required
def dashboard_redirect(request):
    user = request.user
    if user.is_admin:
        return redirect('admin_dashboard')
    elif user.is_organizer:
        return redirect('organizer_dashboard')
    return redirect('attendee_dashboard')

def admin_setup_view(request, token):
    expected = os.environ.get('ADMIN_SETUP_SECRET', '')
    if not expected or token != expected:
        messages.error(request, 'Invalid or expired setup link.')
        return redirect('login')

    if CustomUser.objects.filter(is_superuser=True).exists():
        messages.error(request, 'Admin account already exists. This link is no longer valid.')
        return redirect('login')

    if request.method == 'POST':
        import secrets
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
