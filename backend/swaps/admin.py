from django.contrib import admin
from .models import SwapRequest, SwapSession, SwapRating

@admin.register(SwapRequest)
class SwapRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'skill_offered', 'skill_wanted', 'status', 'created_at')
    list_filter = ('status', 'duration', 'preferred_time', 'created_at')
    search_fields = ('from_user__email', 'to_user__email', 'skill_offered__name', 'skill_wanted__name')

@admin.register(SwapSession)
class SwapSessionAdmin(admin.ModelAdmin):
    list_display = ('swap_request', 'scheduled_date', 'completed', 'created_at')
    list_filter = ('completed', 'created_at')

@admin.register(SwapRating)
class SwapRatingAdmin(admin.ModelAdmin):
    list_display = ('swap_session', 'from_user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
