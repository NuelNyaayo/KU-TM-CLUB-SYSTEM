from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, get_backends
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache
from .models import Leader, ROLE_MAPPING, CustomUser
from django.contrib.auth.hashers import check_password  # Used to verify passwords
from django.contrib.auth.hashers import check_password

def index(request): 

    return render(request, 'index.html')

def login_view(request):  # Renamed from `login` to `login_view`
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, email=email, password=password)  # Use email instead of username

        if user is not None:
            login(request, user)  # Use Django's login function correctly
            # messages.success(request, 'Login success! Welcome.')
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

        # messages.success(request, 'Registration successful! Welcome.')
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

# Leader Dashboard Pages

def leader_login(request):
    if request.method == 'POST':
        member_no = request.POST.get('member-no', '').strip()
        leader_no = request.POST.get('leader-no', '').strip()
        password = request.POST.get('password', '').strip()

        # Ensure all fields are filled
        if not member_no or not leader_no or not password:
            messages.error(request, 'All fields are required.')
            return redirect('leader_login')

        try:
            # Convert member_no to integer to remove leading zeros
            user_id = int(member_no)

            # Retrieve leader and associated user
            leader = Leader.objects.select_related('user').get(
                leader_no=leader_no,
                user__id=user_id
            )
            user = leader.user  

        except (Leader.DoesNotExist, ValueError):
            messages.error(request, 'Invalid Leader Number or Member Number.')
            return redirect('leader_login')

        # Verify the password
        if check_password(password, user.password):
            # Get the first authentication backend
            backends = get_backends()
            if backends:
                backend = backends[0]  # Ensure there's at least one backend
                user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            
            # Log in the user
            login(request, user)
            # messages.success(request, 'Login successful!')

            # **Ensure localStorage is cleared before redirecting**
            response = redirect('leader_dash')
            response.set_cookie('clear_cache', 'true')  # JavaScript will detect this
            return response

        else:
            messages.error(request, 'Incorrect password.')
            return redirect('leader_login')

    return render(request, 'leader_login.html')

def leader_register(request): 
    if request.method == 'POST':
        role = request.POST.get('role', '').strip()
        corporate_email = request.POST.get('corporate_email', '').strip()
        member_no = request.POST.get('member-no', '').strip()
        leader_no = request.POST.get('leader-no', '').strip()

        # Convert role format (uppercase for specific roles, title case otherwise)
        role = role.upper() if role.lower() in ["vpe", "vpm", "vppr", "saa"] else role.title()

        # Debugging: Print role for verification
        print(f"DEBUG: Received role - {role}")

        # Validate role
        if role not in ROLE_MAPPING:
            messages.error(request, f"Invalid role selected: {role}")
            return redirect('leader_register')

        User = get_user_model()

        # Convert member_no to integer (removes leading zeros)
        try:
            user_id = int(member_no)
            user = User.objects.get(id=user_id)
        except (ValueError, User.DoesNotExist):
            messages.error(request, 'You must be a registered member to become a leader.')
            return redirect('leader_register')

        # Ensure corporate email matches the registered email
        if user.email.lower() != corporate_email.lower():
            messages.error(request, 'The email you entered does not match the one registered in the system.')
            return redirect('leader_register')

        # Check if user is already a leader
        if Leader.objects.filter(user=user).exists():
            messages.error(request, 'You are already registered as a leader.')
            return redirect('leader_register')

        # Ensure leader_no is unique
        if Leader.objects.filter(leader_no=leader_no).exists():
            messages.error(request, 'The leader number is already taken. Please enter a unique leader number.')
            return redirect('leader_register')

        # Create Leader record
        leader = Leader.objects.create(user=user, role=role, leader_no=leader_no)
        leader.save()

        # Log in the leader automatically (Ensure authentication backend is set)
        backends = get_backends()
        if backends:
            backend = backends[0]  # Ensure there's at least one backend
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

        login(request, user)

        # messages.success(request, 'Leader registration successful!')

        # **Ensure localStorage is cleared before redirecting**
        response = redirect('leader_dash')
        response.set_cookie('clear_cache', 'true')  # JavaScript will detect this
        return response

    return render(request, 'leader_register.html')


def leader_dash(request): 

    return render(request, 'leader_dash.html', {"current_page": "Dashboard"})

def leader_membership(request): 

    return render(request, 'leader_membership.html', {"current_page": "Membership"})

def leader_attendance(request): 

    return render(request, 'leader_attendance.html', {"current_page": "Attendance"})

def leader_elections(request): 

    return render(request, 'leader_elections.html', {"current_page": "Elections"})



