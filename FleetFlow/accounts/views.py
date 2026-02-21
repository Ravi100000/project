from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegisterForm
from .decorators import role_required
from .models import CustomUser


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    role_demos = [
        ('MANAGER',    'Fleet Manager',   'manager1',    'pass1234',  'bi-shield-lock-fill',  'role-manager'),
        ('DISPATCHER', 'Dispatcher',      'dispatcher1', 'pass1234',  'bi-broadcast',         'role-dispatcher'),
        ('SAFETY',     'Safety Officer',  'safety1',     'pass1234',  'bi-person-badge-fill', 'role-safety'),
        ('FINANCE',    'Financial Analyst','finance1',    'pass1234',  'bi-cash-coin',         'role-finance'),
    ]
    
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        # If a role was selected, ensure the authenticated user matches that role
        selected_role = request.POST.get('role')
        if selected_role and not user.is_superuser and user.role != selected_role:
            messages.error(request, 'Selected role does not match the user account.')
            return render(request, 'accounts/login.html', {'form': form, 'role_demos': role_demos})
        if not user.is_approved:
            messages.error(request, 'Your account is pending admin approval.')
            return render(request, 'accounts/login.html', {'form': form, 'role_demos': role_demos})
        
        login(request, user)
        messages.success(request, f'Welcome back, {user.username}!')
        
        # Check for 'next' parameter for redirection
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
            
        role_redirects = {
            'ADMIN': 'admin-portal',
            'MANAGER': 'dashboard',
            'DISPATCHER': 'trip-list',
            'SAFETY': 'driver-list',
            'FINANCE': 'dashboard',
        }
        target = role_redirects.get(user.role, 'dashboard')
        return redirect(target)
    
    return render(request, 'accounts/login.html', {'form': form, 'role_demos': role_demos})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_approved = False  # Explicitly ensure it's False
        user.save()
        messages.info(request, 'Registration successful! Please wait for an admin to approve your account.')
        return redirect('login')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@role_required('ADMIN')
def admin_portal_view(request):
    unapproved_users = CustomUser.objects.filter(is_approved=False).order_by('-date_joined')
    return render(request, 'accounts/admin_portal.html', {'unapproved_users': unapproved_users})


@login_required
@role_required('ADMIN')
def approve_user_view(request, user_id):
    user_to_approve = get_object_or_404(CustomUser, id=user_id)
    action = request.POST.get('action')
    if action == 'approve':
        user_to_approve.is_approved = True
        user_to_approve.save()
        messages.success(request, f'User {user_to_approve.username} has been approved.')
    elif action == 'reject':
        username = user_to_approve.username
        user_to_approve.delete()
        messages.warning(request, f'User {username} registration has been rejected and deleted.')
    return redirect('admin-portal')


@login_required
def logout_view(request):
    if request.method in ('POST', 'GET'):
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('login')



@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})
