from django.shortcuts import render, redirect
from .forms import CustomRegistrationForm, AssingRoleForm, CreateGroupForm, CustomLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from .forms import UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm


def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect('home')
    return _wrapped_view

def organizer_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.groups.filter(name='Admin').exists() or 
            request.user.groups.filter(name='Organizer').exists()
        ):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Access denied. Organizer privileges required.")
            return redirect('home')
    return _wrapped_view

def participant_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Please log in to continue.")
            return redirect('login')
    return _wrapped_view


def sign_up(request):
    form = CustomRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False  
        user.save()

        token = default_token_generator.make_token(user)

        uid = str(user.pk) 

        domain = get_current_site(request).domain
        activation_link = f'http://{domain}/activate/{uid}/{token}/'


        subject = "Activate Your Account"
        message = render_to_string('activation_email.html', {
            'user': user,
            'activation_link': activation_link,
        })
        send_mail(subject, message, 'from@example.com', [user.email])

        messages.success(request, "Account created! Please check your email to activate your account.")
        return redirect('login') 

    return render(request, 'sign_up.html', {"form": form})



def base_view(request):
    return render(request, 'base.html')

def sign_in(request):
    form = CustomLoginForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html', {'form': form})


def sign_out(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('home')
    return redirect('home')

@login_required
@admin_required
def admin_dashboard(request):
    users = User.objects.all()
    role = request.user.groups.first().name if request.user.groups.exists() else "No Role Assigned"

    context = {
        "role": role,
        "users": users
    }

    return render(request, 'ad_dashboard.html', context)
    

@login_required
@admin_required
def assing_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssingRoleForm(request.POST or None) 
    if request.method == 'POST':
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()
            user.groups.add(role)
            messages.success(request, f"{role.name} has been assigned successfully to {user.username}")
            return redirect('admin-dashboard')
        else:
            messages.error(request, "Invalid form submission. Please check the data.")
    
    return render(request, 'assing_role.html', {"form": form, "user": user})

@login_required
@admin_required
def create_group(request):
    form = CreateGroupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            group = form.save()  
            permissions = form.cleaned_data.get('permissions')
            group.permissions.set(permissions) 
            messages.success(request, f"Group '{group.name}' has been created successfully with selected permissions.")
            return redirect('admin-dashboard') 
        else:
            messages.error(request, "Invalid form submission. Please check the data.")
    
    return render(request, 'create_group.html', {'form': form})


def group_list(request):
    groups = Group.objects.all()
    return render(request, 'group_list.html', {'groups': groups})
        

def activate(request, uid, token):
    try:
        user = User.objects.get(pk=uid)  
    except User.DoesNotExist:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True  
        user.save()
        return redirect('login') 
    else:
        return render(request, 'activation_failed.html')  





@login_required
def profile_view(request):
    """View user profile"""
    return render(request, 'profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    """Update user profile information"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'edit_mode': True
    })

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'profile.html', {'password_form': form, 'password_change_mode': True})

# Password Reset Views - These remain the same as before
class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset.html'
    success_url = reverse_lazy('password_reset_done')
    subject_template_name = 'registration/password_reset_subject.txt'
    email_template_name = 'registration/password_reset_email.html'
    
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
