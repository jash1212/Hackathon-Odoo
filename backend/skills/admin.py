from django.contrib import admin
from .models import Skill, UserSkill

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'skill_type', 'proficiency_level', 'created_at')
    list_filter = ('skill_type', 'proficiency_level', 'skill__category')
    search_fields = ('user__email', 'skill__name')
