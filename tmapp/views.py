from django.shortcuts import render, redirect, reverse, get_object_or_404
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
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import Membership
from .models import Meeting, MeetingRole, Payment
import requests 
from django.utils import timezone
import base64
from datetime import datetime
import json
import threading
import time
from django.utils.timezone import now


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

def memb_dash(request):
    membership, _ = Membership.objects.get_or_create(member=request.user)
    return render(request, 'memb_dash.html', {
        "current_page": "Dashboard",
        "membership": membership
    })


@login_required
def memb_roles(request):
    upcoming_meetings = Meeting.get_upcoming_meetings()
    
    if request.method == "POST":
        meeting_number = request.POST.get("meeting-number")
        availability = request.POST.get("availability")
        role = request.POST.get("role")
        attire = request.POST.get("meeting-attire", "")
        word_of_day = request.POST.get("word-of-day", "")
        speech_project = request.POST.get("speech-project", "")
        speech_title = request.POST.get("speech-title", "")
        evaluated_speech_project = request.POST.get("evaluation-project", "")
        focus_point = request.POST.get("focus-point", "")

        if not meeting_number or not availability:
            messages.error(request, "Please select a meeting and confirm your availability.")
            return redirect("memb_roles")

        meeting = Meeting.objects.filter(meeting_number=meeting_number).first()
        if not meeting:
            messages.error(request, "Invalid meeting selected.")
            return redirect("memb_roles")

        # If user is not available, mark as absent
        if availability == "no":
            MeetingRole.objects.create(meeting=meeting, member=request.user, role="Attendee", is_absent=True)
            messages.success(request, "Your absence has been recorded.")
            return redirect("memb_roles")

        if not role:
            messages.error(request, "Please select a role if you are available.")
            return redirect("memb_roles")

        # Check if role is already taken
        if MeetingRole.objects.filter(meeting=meeting, role=role).exists():
            messages.error(request, "This role is already taken for the selected meeting.")
            return redirect("memb_roles")

        # Create the MeetingRole entry
        meeting_role = MeetingRole(
            meeting=meeting,
            member=request.user,
            role=role,
            meeting_attire=attire if role == "TMOD" else "",
            word_of_the_day=word_of_day if role == "Grammarian" else "",
            speech_project=speech_project if role == "CC_Speaker" else "",
            speech_title=speech_title if role == "CC_Speaker" else "",
            evaluated_speech_project=evaluated_speech_project if role == "Evaluator" else "",
            focus_point=focus_point if role == "General_Evaluator" else "",
            is_absent=False
        )

        try:
            meeting_role.save()
            messages.success(request, "Your role has been successfully assigned!")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect("memb_roles")

    return render(request, "memb_roles.html", {
        "current_page": "Roles",
        "meetings": upcoming_meetings,
        "meeting_roles": MeetingRole.ROLE_CHOICES,  # Pass ROLE_CHOICES instead of QuerySet
    })

def get_available_roles(request, meeting_number):
    meeting = get_object_or_404(Meeting, meeting_number=meeting_number)
    taken_roles = MeetingRole.objects.filter(meeting=meeting).values_list('role', flat=True)
    all_roles = dict(MeetingRole.ROLE_CHOICES).keys()
    available_roles = [role for role in all_roles if role not in taken_roles]

    return JsonResponse(available_roles, safe=False)


def get_access_token():
    """Obtain M-Pesa access token"""
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    # Encode credentials
    credentials = f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {"Authorization": f"Basic {encoded_credentials}"}
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("access_token")
    
    print("⚠️ ERROR: Could not obtain access token")
    return None

def format_phone_number(phone):
    """Convert phone number from 07... format to 2547... format"""
    if phone.startswith("07"):
        return "254" + phone[1:]  # Replace '07' with '2547'
    elif phone.startswith("+254"):
        return phone[1:]  # Remove '+'
    elif phone.startswith("254"):
        return phone  # Already correct
    else:
        raise ValueError("Invalid phone number format. Use 07..., 254..., or +254...")

def stk_push(phone, amount, transaction_id):
    """Initiate STK push"""
    try:
        phone = format_phone_number(phone)  # Ensure correct format
    except ValueError as e:
        print("⚠️ ERROR:", str(e))
        return {"error": str(e)}

    access_token = get_access_token()
    if not access_token:
        print("⚠️ ERROR: Could not obtain access token")
        return {"error": "Failed to obtain access token"}

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()).decode()

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.CALLBACK_URL,
        "AccountReference": "TMPayment",
        "TransactionDesc": "Toastmasters Membership Fee"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        # Start a background thread to update status after 15 seconds
        threading.Thread(target=update_payment_status, args=(transaction_id,), daemon=True).start()

    try:
        return response.json()
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from M-Pesa API", "response_text": response.text}
    
    


def memb_membership(request):
    if request.method == "POST":
        payment_plan = request.POST.get("payment_plan")
        payment_method = request.POST.get("payment_method")
        phone_number = request.POST.get("phone_number")
        amount = request.POST.get("amount")

        if not all([payment_plan, payment_method, phone_number, amount]):
            messages.error(request, "All fields are required.")
            return redirect("memb_membership")

        try:
            amount = int(amount)  # Convert amount to integer
        except ValueError:
            messages.error(request, "Invalid amount format.")
            return redirect("memb_membership")

        transaction_id = f"TXN{timezone.now().strftime('%Y%m%d%H%M%S')}"

        if payment_method == "mpesa":
            response = stk_push(phone_number, amount, transaction_id)

            if response.get("ResponseCode") == "0":
                Payment.objects.create(
                    member=request.user,
                    amount=amount,
                    payment_plan=payment_plan,
                    mpesa_transaction_id=transaction_id,
                    payment_status="Pending"
                )
                messages.success(request, "Payment request sent to your phone. Please complete the payment.")
            else:
                error_message = response.get("error", "Failed to initiate M-Pesa payment. Try again.")
                messages.error(request, error_message)

        return redirect("memb_membership")

    return render(request, "memb_membership.html", {"current_page": "Membership"})

def check_payment_status(request):
    payment = Payment.objects.filter(member=request.user, payment_status="Paid").order_by("-payment_date", "-payment_time").first()
    
    if payment:
        return JsonResponse({
            "status": payment.payment_status,
            "transaction_id": payment.mpesa_transaction_id,
            "amount": payment.amount,
            "date": payment.payment_date.strftime("%d %b %Y"),
            "time": payment.payment_time.strftime("%H:%M:%S"),
            "plan": payment.get_payment_plan_display()
        })
    
    return JsonResponse({"status": "Pending"})

def update_payment_status(transaction_id):
    """Simulate payment confirmation after 15 seconds"""
    time.sleep(0)
    payment = Payment.objects.filter(mpesa_transaction_id=transaction_id, payment_status="Pending").first()
    if payment:
        payment.payment_status = "Paid"
        payment.save()
        payment.member.membership.activate_membership()


# @csrf_exempt
# def mpesa_callback(request):
#     try:
#         data = json.loads(request.body.decode("utf-8"))

#         print("🔍 CALLBACK DATA:", json.dumps(data, indent=4))  # Debugging

#         if "Body" in data and "stkCallback" in data["Body"]:
#             transaction_id = data["Body"]["stkCallback"].get("CheckoutRequestID")
#             result_code = data["Body"]["stkCallback"].get("ResultCode", -1)

#             payment = Payment.objects.filter(mpesa_transaction_id=transaction_id).first()

#             if payment:
#                 payment.payment_status = "Paid" if result_code == 0 else "Failed"
#                 payment.save()

#         return JsonResponse({"message": "Callback received"}, status=200)

#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Invalid JSON received"}, status=400)

def memb_resources(request): 

    return render(request, 'memb_resources.html', {"current_page": "Resources"})

def memb_notifications(request): 

    return render(request, 'memb_notifications.html', {"current_page": "Notifications"})

def memb_elections(request): 

    return render(request, 'memb_elections.html', {"current_page": "Elections"})

@login_required
def memb_profile(request):
    CustomUser = get_user_model()
    user = CustomUser.objects.get(pk=request.user.pk)  # Ensure fetching from CustomUser model
    return render(request, 'memb_profile.html', {
        "current_page": "Profile",
        "user": user
    })

@login_required  # Ensure only logged-in users can update profile pictures
def update_profile_picture(request):
    if request.method == "POST" and request.FILES.get("profile_picture"):
        user = request.user
        profile_pic = request.FILES["profile_picture"]

        # Save the file with a unique name
        file_path = f"profile_pics/{user.id}_{profile_pic.name}"
        saved_path = default_storage.save(file_path, ContentFile(profile_pic.read()))

        # Construct the full URL for the saved image
        image_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)

        # Update user's profile picture in the database
        user.profile_picture = saved_path
        user.save()

        return JsonResponse({"success": True, "image_url": image_url})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def memb_settings(request):
    user = request.user  # Get logged-in user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.phone_number = request.POST.get('phone_number', '').strip()
        user.dob = request.POST.get('dob', '').strip() or None  # Handle empty DOB
        
        user.save()
        messages.success(request, 'Your account settings have been updated successfully!')
        return redirect('memb_settings')

    return render(request, 'memb_settings.html', {
        "current_page": "Settings",
        "user": user
    })


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



