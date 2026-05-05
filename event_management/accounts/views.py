from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import RegisterForm, LoginForm
from .models import CustomUser
from .utils import send_verification_email


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(user, request)
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('email_verification_sent')
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
            if not user.is_email_verified:
                messages.error(request, 'Please verify your email address before logging in. Check your email for the verification link or request a new one.')
                return render(request, 'accounts/login.html', {'form': form})
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
