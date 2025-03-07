from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache
from .mpesa.core import MpesaClient


client = MpesaClient()
callback_url = "https://api.darajambili.co.ke/express-payment"


def index(request): 

    return render(request, 'index.html')

def login_view(request):  # Renamed from `login` to `login_view`
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, email=email, password=password)  # Use email instead of username

        if user is not None:
            login(request, user)  # Use Django's login function correctly
            messages.success(request, 'Login success! Welcome.')
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

        messages.success(request, 'Registration successful! Welcome.')
        return redirect('memb_dash')

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

    return render(request, 'memb_dash.html', {"current_page": "Dashboard"})


def memb_roles(request): 

    return render(request, 'memb_roles.html', {"current_page": "Roles"})

def memb_membership(request): 
    if request.method == 'POST':
        amount = request.POST.get('amount', '').strip()
        amount = int(amount)
        phone_number = request.POST.get('phone_number', '').strip()
        account_ref = "PAYMENT001"
        trans_desc = "my payment...."

        client.stk_push(phone_number,amount,account_ref,trans_desc,callback_url)
        return render(request, 'memb_membership.html', {"current_page": "Membership"})

    return render(request, 'memb_membership.html', {"current_page": "Membership"})

def memb_resources(request): 

    return render(request, 'memb_resources.html', {"current_page": "Resources"})

def memb_notifications(request): 

    return render(request, 'memb_notifications.html', {"current_page": "Notifications"})

def memb_elections(request): 

    return render(request, 'memb_elections.html', {"current_page": "Elections"})

def memb_profile(request): 

    return render(request, 'memb_profile.html', {"current_page": "Profile"})

def memb_settings(request): 

    return render(request, 'memb_settings.html', {"current_page": "Settings"})

def memb_contact(request): 

    return render(request, 'memb_contact.html', {"current_page": "Contact"})

def memb_support(request): 

    return render(request, 'memb_support.html', {"current_page": "Support"})

