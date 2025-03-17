from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Leader


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


