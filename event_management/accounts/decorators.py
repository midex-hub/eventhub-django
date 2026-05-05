from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

def role_required(role):
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            if role == 'admin' and not (request.user.is_admin):
                messages.error(request, 'Access denied.')
                return redirect('home')
            if role == 'organizer' and not (request.user.is_organizer or request.user.is_admin):
                messages.error(request, 'Access denied.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
