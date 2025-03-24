from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import  (CustomUser, Leader, Membership, Payment, Meeting, MeetingRole, Resource,
    Election, Nomination, Candidate, Vote, Notification,
    LeaderReport, NominationVote)


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
@admin.register(MeetingRole)
class MeetingRoleAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'member', 'role')
    list_filter = ('role', 'meeting')
    search_fields = ('meeting__meeting_number', 'member__username')

# Customizing Leader Report Admin
@admin.register(LeaderReport)
class LeaderReportAdmin(admin.ModelAdmin):
    list_display = ('leader', 'report_type', 'created_at')
    list_filter = ('report_type',)
    search_fields = ('leader__username',)



