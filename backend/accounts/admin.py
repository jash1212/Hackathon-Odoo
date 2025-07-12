from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PlatformMessage, UserReport, SkillReport

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_banned', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_banned', 'created_at', 'experience_level')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('bio', 'location', 'avatar', 'availability', 'experience_level', 'response_time', 'rating', 'completed_swaps')
        }),
        ('Admin Information', {
            'fields': ('is_banned', 'ban_reason', 'ban_date', 'banned_by')
        }),
    )
    
    readonly_fields = ('rating', 'completed_swaps', 'ban_date')

@admin.register(PlatformMessage)
class PlatformMessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'message_type', 'is_active', 'created_by', 'created_at')
    list_filter = ('message_type', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'created_by__username')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Message Content', {
            'fields': ('title', 'content', 'message_type')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported_user', 'report_type', 'status', 'created_at')
    list_filter = ('report_type', 'status', 'created_at')
    search_fields = ('reporter__username', 'reported_user__username', 'description')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Report Details', {
            'fields': ('reporter', 'reported_user', 'report_type', 'description', 'evidence')
        }),
        ('Admin Review', {
            'fields': ('status', 'admin_notes', 'resolved_by', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            if obj.status in ['resolved', 'dismissed']:
                obj.resolved_by = request.user
                from django.utils import timezone
                obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)

@admin.register(SkillReport)
class SkillReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'skill', 'report_type', 'status', 'created_at')
    list_filter = ('report_type', 'status', 'created_at')
    search_fields = ('reporter__username', 'skill__name', 'description')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Report Details', {
            'fields': ('reporter', 'skill', 'report_type', 'description')
        }),
        ('Admin Review', {
            'fields': ('status', 'admin_notes', 'resolved_by', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            if obj.status in ['approved', 'rejected', 'skill_removed']:
                obj.resolved_by = request.user
                from django.utils import timezone
                obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)
