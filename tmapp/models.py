from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model
import re
from django.utils.timezone import now
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta 
from django.utils import timezone
from django.core.exceptions import ValidationError


# 1. CustomUserManager Model
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Remove fields that are required for regular users but not superusers
        extra_fields.pop('phone_number', None)
        extra_fields.pop('registration_number', None)
        extra_fields.pop('dob', None)

        return self.create_user(email, password, **extra_fields)


# 2. CustomUser Model
class CustomUser(AbstractUser):
    username = None  
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    registration_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_initials(self):
        first = self.first_name[0] if self.first_name else ""
        last = self.last_name[0] if self.last_name else ""
        return (first + last).upper() if first or last else "U"



User = get_user_model()

# Mapping of roles to role numbers
ROLE_MAPPING = {
    "President": "001",
    "VPE": "002",
    "VPM": "003",
    "VPPR": "004",
    "Treasurer": "005",
    "Secretary": "006",
    "SAA": "007",
}

# 3. Leader Model
class Leader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[(key, key) for key in ROLE_MAPPING.keys()])
    leader_no = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        # Validate leader_no format (must be ROLE_NUMBER/YEAR, e.g., 001/2021)
        pattern = r"^\d{3}/\d{4}$"
        if not re.match(pattern, self.leader_no):
            raise ValueError("Leader number must follow the format ROLE_NUMBER/YEAR (e.g., 001/2021).")

        # Extract role number from leader_no and validate against the role
        try:
            role_number, year = self.leader_no.split('/')
        except ValueError:
            raise ValueError("Leader number format is incorrect. Use ROLE_NUMBER/YEAR (e.g., 001/2021).")

        # Validate role number against the selected role
        expected_role_number = ROLE_MAPPING.get(self.role)
        if expected_role_number is None:
            raise ValueError("Invalid role selected.")

        if role_number != expected_role_number:
            raise ValueError(f"Invalid leader number for the selected role. Expected {expected_role_number}/YEAR.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.role} ({self.leader_no})"
    

# 4. Membership Model
class Membership(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Expired', 'Expired'),
    ]

    member = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Inactive')
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.member.email} - {self.status}"

    def activate_membership(self, duration_in_days=180):
        """Activates membership and sets expiry date"""
        self.status = 'Active'
        self.expiry_date = now().date() + timedelta(days=duration_in_days)
        self.save()

    def check_and_update_status(self):
        """Automatically updates membership status if expired"""
        if self.expiry_date and self.expiry_date < now().date():
            self.status = 'Expired'
            self.save()

# Signal to create Membership when a User is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_membership(sender, instance, created, **kwargs):
    if created:
        Membership.objects.create(member=instance)



# 5. Payment Model
class Payment(models.Model):
    PLAN_CHOICES = [
        ('Semester', 'Ksh300 per semester'),
        ('Yearly', 'Ksh550 per academic year'),
        ('Daily', 'Ksh1 per day'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    payment_plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    mpesa_transaction_id = models.CharField(max_length=50, unique=True)
    payment_date = models.DateField(auto_now_add=True)  # Stores payment date
    payment_time = models.TimeField(auto_now_add=True, null=True)  # Stores payment time
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')  # Default is 'Pending'

    def __str__(self):
        return f"{self.member.username} - {self.amount} - {self.payment_plan} - {self.payment_status}"


# 6. Meeting Model
class Meeting(models.Model):
    STATUS_CHOICES = [
        ("Upcoming", "Upcoming Meeting"),
        ("Ongoing", "Ongoing Meeting"),
        ("Previous", "Previous Meeting"),
    ]

    meeting_number = models.CharField(max_length=20, unique=True)
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=255)  # Specifies where the meeting took place
    theme = models.CharField(max_length=255)  # Specifies what the meeting was about

    attendees = models.ManyToManyField(User, related_name='attended_meetings', blank=True)
    absentees = models.ManyToManyField(User, related_name='missed_meetings', blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Upcoming")  # Status field

    @staticmethod
    def get_upcoming_meetings():
        """Fetch only meetings that are in the future or today."""
        return Meeting.objects.filter(date__gte=timezone.now().date()).order_by('date')

    def update_status(self):
        """Automatically updates the meeting status based on the current time."""
        now = timezone.localtime(timezone.now())  # Get current date & time in local timezone
        meeting_datetime = timezone.make_aware(timezone.datetime.combine(self.date, self.time))  # Meeting start datetime
        meeting_end_time = meeting_datetime + timezone.timedelta(hours=2, minutes=30)  # 2.5-hour duration

        if meeting_datetime <= now <= meeting_end_time:
            self.status = "Ongoing"
        elif now < meeting_datetime:
            self.status = "Upcoming"
        else:
            self.status = "Previous"

    def save(self, *args, **kwargs):
        """Override save method to ensure status updates before saving."""
        self.update_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Meeting {self.meeting_number} - {self.date} - {self.venue} - Theme: {self.theme} - Status: {self.status}"



# 7. Meeting Role Model
class MeetingRole(models.Model):
    ROLE_CHOICES = [
        ('TMOD', 'Toastmaster of the Day'),
        ('CC_Speaker', 'CC Speaker'),
        ('Evaluator', 'Speech Evaluator'),
        ('General_Evaluator', 'General Evaluator'),
        ('Table_Topics_Master', 'Table Topics Master'),
        ('Hack_Master', 'Hack Master'),
        ('Joke_Master', 'Joke Master'),
        ('Timer', 'Timer'),
        ('Grammarian', 'Grammarian'),
        ('Ah_Counter', 'Ah Counter'),
        ('Attendee', 'Attendee'),
    ]

    SPEECH_PROJECT_CHOICES = [(f'CC{i}', f'CC{i}') for i in range(1, 11)]  # ('CC1', 'CC1') to ('CC10', 'CC10')

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='roles')
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_roles')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)

    # TMOD specific field (optional)
    meeting_attire = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., Formal, Casual, Kitenge")

    # CC Speaker Fields
    speech_project = models.CharField(max_length=10, choices=SPEECH_PROJECT_CHOICES, blank=True, null=True, help_text="Specify CC project (e.g., CC1 - CC10)")
    speech_title = models.CharField(max_length=255, blank=True, null=True, help_text="Optional speech title")

    # Evaluator Fields
    evaluated_speech_project = models.CharField(max_length=10, choices=SPEECH_PROJECT_CHOICES, blank=True, null=True, help_text="Specify CC project evaluated (e.g., CC1 - CC10)")

    # Grammarian field (optional word of the day)
    word_of_the_day = models.CharField(max_length=50, blank=True, null=True, help_text="Optional Word of the Day")

    # General Evaluator field (optional focus point)
    focus_point = models.CharField(max_length=255, blank=True, null=True, help_text="Optional evaluation focus (e.g., timing, filler words)")

    # Absentee tracking
    is_absent = models.BooleanField(default=False, help_text="Mark as absent if not attending")

    class Meta:
        unique_together = ('meeting', 'member')  # Prevents duplicate roles for the same member in a meeting

    def get_available_cc_speech_projects(self):
        """Fetches CC Speaker projects from the same meeting, marking already assigned ones as unavailable."""
        available_projects = list(MeetingRole.objects.filter(
            meeting=self.meeting, role='CC_Speaker'
        ).exclude(speech_project__isnull=True).exclude(speech_project="")
        .values_list('speech_project', flat=True).distinct())

        assigned_projects = list(MeetingRole.objects.filter(
            meeting=self.meeting, role='Evaluator'
        ).exclude(pk=self.pk).values_list('evaluated_speech_project', flat=True))

        return [(project, project, project in assigned_projects) for project in available_projects]  # (value, label, disabled)

    def clean(self):
        """Custom validation rules"""
        if self.role == 'CC_Speaker' and not self.speech_project:
            raise ValidationError({'speech_project': "CC Speakers must select a speech project."})

        if self.role == 'Evaluator':
            if not self.evaluated_speech_project:
                raise ValidationError({'evaluated_speech_project': "Evaluators must specify a project to evaluate."})

            available_speech_projects = [proj[0] for proj in self.get_available_cc_speech_projects()]

            if self.evaluated_speech_project not in available_speech_projects:
                raise ValidationError({'evaluated_speech_project': "Selected speech project is not assigned to any CC Speaker in this meeting or already taken."})

    def save(self, *args, **kwargs):
        """Ensure validation runs before saving."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.meeting.meeting_number} - {self.member.email} - {self.role}"





# 8. Resource Model
class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('Document', 'Document'),
        ('Video', 'Video'),
        ('Website', 'Website'),
        ('Audio', 'Audio'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # Added description field
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPE_CHOICES)
    url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(User, related_name='resources')

    def __str__(self):
        return self.title



# 9. Election Model
class Election(models.Model):
    academic_year = models.CharField(max_length=9, unique=True)  # e.g., "2024/2025"
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Election {self.academic_year}"

    def total_voters(self):
        """Returns the number of unique voters in this election."""
        return Vote.objects.filter(candidate__position__election=self).values('voter').distinct().count()



# 10. Nomination Model
class Nomination(models.Model):
    academic_year = models.CharField(max_length=9, unique=True)  # e.g., "2024/2025"
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Nomination {self.academic_year}"

    def total_nominators(self):
        """Returns the number of unique nominators in this nomination."""
        return NominationVote.objects.filter(candidate__position__nomination=self).values('nominator').distinct().count()




# 11. Candidate Model
class Candidate(models.Model):
    POSITION_CHOICES = [
        ('President', 'President'),
        ('VPE', 'Vice President Education'),
        ('VPM', 'Vice President Membership'),
        ('VPPR', 'Vice President Public Relations'),
        ('Secretary', 'Secretary'),
        ('Treasurer', 'Treasurer'),
        ('SAA', 'Sergeant At Arms'),
    ]

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidacies')
    nomination = models.ForeignKey(Nomination, on_delete=models.CASCADE, related_name='candidates', null=True, blank=True)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates', null=True, blank=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)

    class Meta:
        unique_together = ('nomination', 'position', 'member')

    def __str__(self):
        return f"{self.member.username} - {self.position} - {self.nomination.academic_year}"

    def is_elected(self):
        """Check if this candidate has won the election for their position."""
        return Vote.objects.filter(candidate=self).count() > 0  # Modify logic if needed

# 12. Vote Model
class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')  # The member who voted
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')  # Candidate who got the vote
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='votes')  # Election the vote belongs to
    timestamp = models.DateTimeField(auto_now_add=True)  # Records when the vote was cast

    class Meta:
        unique_together = ('voter', 'election', 'candidate')  # Ensures a voter votes only once per candidate in an election

    def __str__(self):
        return f"{self.voter.username} → {self.candidate.member.username} ({self.candidate.position.name}) in {self.election.academic_year}"



# 13. Notification Model
class Notification(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.member.username} - {self.message}"


# 14. Leader Report Model
class LeaderReport(models.Model):
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leader_reports')
    report_type = models.CharField(max_length=50)  # Membership, Attendance, Election, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Stores report details

    def __str__(self):
        return f"{self.leader.username} - {self.report_type} Report"
    

# 15. NominationVote Model
class NominationVote(models.Model):
    nominator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nominations_made')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='nominations_received')
    nomination = models.ForeignKey(Nomination, on_delete=models.CASCADE, related_name='nominations')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('nominator', 'nomination', 'candidate')

    def __str__(self):
        return f"{self.nominator.username} nominated {self.candidate.member.username} in {self.nomination.academic_year}"
