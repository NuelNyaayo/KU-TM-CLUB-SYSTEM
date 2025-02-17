from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache


def index(request): 

    return render(request, 'index.html')

def login_view(request):  # Renamed from `login` to `login_view`
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, email=email, password=password)  # Use email instead of username

        if user is not None:
            login(request, user)  # Use Django's login function correctly
            return redirect('memb_dash')  # Redirect to homepage
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')

    return render(request, 'login.html')

def registration(request): 
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        corporate_email = request.POST.get('corporate_email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        registration_number = request.POST.get('registration_number', '').strip()
        dob = request.POST.get('dob', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        remember = request.POST.get('remember', 'off')  # Default to 'off' if not checked

        User = get_user_model()

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('registration')

        if User.objects.filter(email=corporate_email).exists():  # Use `email` instead of `corporate_email`
            messages.error(request, 'Corporate Email is already registered')
            return redirect('registration')

        if User.objects.filter(registration_number=registration_number).exists():
            messages.error(request, 'Registration Number is already registered')
            return redirect('registration')

        # Create new user
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=corporate_email,  # Use `email` instead of `corporate_email`
            phone_number=phone_number,
            registration_number=registration_number,
            dob=dob,
            password=password
        )

        user.save()

        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')

    return render(request, 'registration.html')

    
def logout_view(request):
    logout(request)
    return redirect('/')  # Redirect to the login page after logout

def verify(request): 

    return render(request, 'verify.html')

# @never_cache
def memb_dash(request):
    # if not request.user.is_authenticated:
    #     return redirect('login')  # Redirect to login if not authenticated 

    return render(request, 'memb_dash.html')


def memb_roles(request): 

    return render(request, 'memb_roles.html')

def memb_membership(request): 

    return render(request, 'memb_membership.html')

def memb_resources(request): 

    return render(request, 'memb_resources.html')

