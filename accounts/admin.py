from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPCode

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_email_verified', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_email_verified']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('phone_number', 'is_email_verified', 'is_phone_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('email', 'phone_number')
        }),
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'purpose', 'otp_type', 'is_used', 'created_at', 'expires_at']
    list_filter = ['purpose', 'otp_type', 'is_used', 'created_at']
    search_fields = ['user__email', 'user__username', 'code']
    readonly_fields = ['code', 'created_at', 'expires_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        # Empêcher l'ajout manuel d'OTP depuis l'admin
        return False