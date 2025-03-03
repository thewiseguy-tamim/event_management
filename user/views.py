from django.shortcuts import render, redirect
from .forms import CustomRegistrationForm, AssingRoleForm, CreateGroupForm, CustomLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

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

        # Send activation email
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
def admin_dashboard(request):
    users = User.objects.all()
    role = None

    if request.user.groups.filter(name="Admin").exists():
        role = "Admin"
    elif request.user.groups.filter(name="Organizer").exists():
        role = "Organizer"
    elif request.user.groups.filter(name="Participant").exists():
        role = "Participant"

    context = {
        "role": role,
        "users": users
    }

    return render(request, 'ad_dashboard.html', context)
    

def assing_role(request, user_id):
    user = User.objects.get(id = user_id)
    form = AssingRoleForm()
    if request.method == 'POST':
        form = AssingRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()
            user.groups.add(role)
            messages.success(request, f"{role.name} has been assigned successfully to {user.first_name}")
            return redirect('admin-dashboard')
        
    return render(request, 'assing_role.html', {"form": form, "user": user})

def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created successfully")
            return redirect('create_group')

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



    

