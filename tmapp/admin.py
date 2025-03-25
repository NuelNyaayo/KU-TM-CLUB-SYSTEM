from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import  (CustomUser, Leader, Membership, Payment, Meeting, MeetingRole, Resource,
    Election, Nomination, Candidate, Vote, Notification,
    LeaderReport, NominationVote)
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms



# Register your models here.

class CustomUserAdmin(UserAdmin):
    ordering = ['email']  # Fix: Order by email instead of username
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'registration_number', 'dob', 'is_staff', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'registration_number', 'dob')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'registration_number', 'dob', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    search_fields = ('email', 'first_name', 'last_name', 'phone_number', 'registration_number')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Leader)

# Simple model registrations
# admin.site.register(Membership)
# admin.site.register(Payment)
# admin.site.register(Meeting)
# admin.site.register(MeetingRole)
admin.site.register(Resource)
admin.site.register(Election)
admin.site.register(Nomination)
# admin.site.register(Candidate)
admin.site.register(Vote)
admin.site.register(Notification)
# admin.site.register(LeaderReport)
admin.site.register(NominationVote)

# Customizing the Candidate model in admin
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('member', 'position', 'nomination', 'election')
    list_filter = ('position', 'nomination', 'election')
    search_fields = ('member__username', 'position')

# Customizing Meeting Admin
@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('meeting_number', 'date', 'venue', 'theme')
    list_filter = ('date', 'venue')
    search_fields = ('meeting_number', 'theme')

# Customizing Payment Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'payment_plan', 'payment_status', 'payment_date')
    list_filter = ('payment_status', 'payment_plan')
    search_fields = ('member__username', 'mpesa_transaction_id')

# Customizing Membership Admin
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'status', 'expiry_date')
    list_filter = ('status',)
    search_fields = ('member__username',)

# Customizing Meeting Role Admin
class MeetingRoleAdminForm(forms.ModelForm):
    """Custom form for MeetingRole to dynamically filter evaluated_speech_project"""
    class Meta:
        model = MeetingRole
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and hasattr(self.instance, 'meeting') and self.instance.meeting and self.instance.role == 'Evaluator':
            meeting = self.instance.meeting

            # Get only CC Speaker projects that have been selected in this meeting
            cc_speech_projects = MeetingRole.objects.filter(
                meeting=meeting,
                role="CC_Speaker"
            ).exclude(speech_project__isnull=True).exclude(speech_project="") \
            .values_list('speech_project', flat=True).distinct()

            # Get already assigned projects to other evaluators
            assigned_projects = MeetingRole.objects.filter(
                meeting=meeting,
                role="Evaluator"
            ).exclude(pk=self.instance.pk).values_list('evaluated_speech_project', flat=True)

            # Construct choice tuples
            choices = []
            for project in cc_speech_projects:
                if project in assigned_projects:
                    choices.append((project, f"{project} (Already Assigned)"))
                else:
                    choices.append((project, project))  # Regular selectable option

            self.fields['evaluated_speech_project'].choices = [('', 'Select a speech project')] + choices

@admin.register(MeetingRole)
class MeetingRoleAdmin(admin.ModelAdmin):
    form = MeetingRoleAdminForm  # Set the custom form
    list_display = ('meeting', 'member', 'role', 'speech_project', 'evaluated_speech_project')
    list_filter = ('role', 'meeting')
    search_fields = ('meeting__meeting_number', 'member__username')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Dynamically filter Evaluator speech project options"""
        if db_field.name == "evaluated_speech_project":
            obj_id = request.resolver_match.kwargs.get('object_id')
            if obj_id:
                try:
                    obj = MeetingRole.objects.get(pk=obj_id)

                    # Get CC Speaker projects from the same meeting (exclude empty/null values)
                    cc_speech_projects = MeetingRole.objects.filter(
                        meeting=obj.meeting,
                        role="CC_Speaker"
                    ).exclude(speech_project__isnull=True).exclude(speech_project="") \
                    .values_list('speech_project', flat=True).distinct()

                    # Get already assigned projects to other evaluators
                    assigned_projects = MeetingRole.objects.filter(
                        meeting=obj.meeting,
                        role="Evaluator"
                    ).exclude(pk=obj.pk).values_list('evaluated_speech_project', flat=True)

                    # Filter queryset to only include unassigned CC projects
                    if not cc_speech_projects:
                        kwargs["queryset"] = MeetingRole.objects.none()
                    else:
                        kwargs["queryset"] = MeetingRole.objects.filter(
                            meeting=obj.meeting,
                            role="CC_Speaker",
                            speech_project__in=[proj for proj in cc_speech_projects if proj not in assigned_projects]
                        )
                except ObjectDoesNotExist:
                    pass  # Prevents crashes if object doesn't exist

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def clean(self):
        """Ensure Evaluators can only evaluate existing CC projects"""
        if self.role == 'Evaluator':
            available_speech_projects = MeetingRole.objects.filter(
                meeting=self.meeting, role='CC_Speaker'
            ).exclude(speech_project__isnull=True).exclude(speech_project="") \
            .values_list('speech_project', flat=True)

            if not available_speech_projects:
                raise ValidationError(_('No CC projects available for evaluation in this meeting. Please select a different role.'))

            if self.evaluated_speech_project not in available_speech_projects:
                raise ValidationError(_('Selected speech project is not assigned to any CC Speaker in this meeting.'))

        super().clean()


# Customizing Leader Report Admin
@admin.register(LeaderReport)
class LeaderReportAdmin(admin.ModelAdmin):
    list_display = ('leader', 'report_type', 'created_at')
    list_filter = ('report_type',)
    search_fields = ('leader__username',)



