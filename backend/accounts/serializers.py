from rest_framework import serializers
from django.contrib.auth import authenticate, login, logout
from .models import User, PlatformMessage, UserReport, SkillReport
from skills.models import Skill
from swaps.models import SwapRequest, SwapSession, SwapRating
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    skills_offered = serializers.SerializerMethodField()
    skills_wanted = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'bio', 'location', 'avatar', 'availability', 'experience_level',
            'response_time', 'rating', 'completed_swaps', 'created_at',
            'skills_offered', 'skills_wanted', 'is_staff', 'is_superuser'
        )
        read_only_fields = ('id', 'email', 'rating', 'completed_swaps', 'created_at', 'is_staff', 'is_superuser')
    
    def get_skills_offered(self, obj):
        from skills.models import UserSkill
        skills = UserSkill.objects.filter(user=obj, skill_type='offered')
        return [skill.skill.name for skill in skills]
    
    def get_skills_wanted(self, obj):
        from skills.models import UserSkill
        skills = UserSkill.objects.filter(user=obj, skill_type='wanted')
        return [skill.skill.name for skill in skills]

class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    skills_offered = serializers.SerializerMethodField()
    skills_wanted = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'full_name', 'avatar', 'location', 'availability',
            'rating', 'skills_offered', 'skills_wanted', 'bio'
        )
    
    def get_skills_offered(self, obj):
        from skills.models import UserSkill
        skills = UserSkill.objects.filter(user=obj, skill_type='offered')
        return [skill.skill.name for skill in skills]
    
    def get_skills_wanted(self, obj):
        from skills.models import UserSkill
        skills = UserSkill.objects.filter(user=obj, skill_type='wanted')
        return [skill.skill.name for skill in skills]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 'location', 
                 'avatar', 'availability', 'experience_level', 'response_time', 'rating', 
                 'completed_swaps', 'created_at', 'is_banned', 'ban_reason', 'ban_date']
        read_only_fields = ['id', 'created_at', 'rating', 'completed_swaps']

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'rating', 'completed_swaps']

class PlatformMessageSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = PlatformMessage
        fields = ['id', 'title', 'content', 'message_type', 'is_active', 
                 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.full_name', read_only=True)
    reported_user_name = serializers.CharField(source='reported_user.full_name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.full_name', read_only=True)
    
    class Meta:
        model = UserReport
        fields = ['id', 'reporter', 'reporter_name', 'reported_user', 'reported_user_name',
                 'report_type', 'description', 'evidence', 'status', 'admin_notes',
                 'resolved_by', 'resolved_by_name', 'resolved_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SkillReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.full_name', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.full_name', read_only=True)
    
    class Meta:
        model = SkillReport
        fields = ['id', 'reporter', 'reporter_name', 'skill', 'skill_name',
                 'report_type', 'description', 'status', 'admin_notes',
                 'resolved_by', 'resolved_by_name', 'resolved_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin user management"""
    total_swaps = serializers.SerializerMethodField()
    total_reports_received = serializers.SerializerMethodField()
    total_reports_made = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 'location',
                 'rating', 'completed_swaps', 'created_at', 'is_banned', 'ban_reason', 
                 'ban_date', 'banned_by', 'total_swaps', 'total_reports_received', 'total_reports_made']
        read_only_fields = ['id', 'created_at', 'rating', 'completed_swaps']
    
    def get_total_swaps(self, obj):
        return SwapRequest.objects.filter(
            Q(from_user=obj) | Q(to_user=obj)
        ).count()
    
    def get_total_reports_received(self, obj):
        return UserReport.objects.filter(reported_user=obj).count()
    
    def get_total_reports_made(self, obj):
        return UserReport.objects.filter(reporter=obj).count()

class AdminDashboardSerializer(serializers.Serializer):
    """Serializer for admin dashboard statistics"""
    total_users = serializers.IntegerField()
    total_swaps = serializers.IntegerField()
    total_reports = serializers.IntegerField()
    total_skill_reports = serializers.IntegerField()
    pending_reports = serializers.IntegerField()
    pending_skill_reports = serializers.IntegerField()
    banned_users = serializers.IntegerField()
    active_messages = serializers.IntegerField()
    
    # Recent activity
    recent_users = serializers.ListField()
    recent_swaps = serializers.ListField()
    recent_reports = serializers.ListField()
    
    # Charts data
    user_growth = serializers.ListField()
    swap_stats = serializers.DictField()
    report_stats = serializers.DictField()

class SwapStatsSerializer(serializers.Serializer):
    """Serializer for swap statistics"""
    total_swaps = serializers.IntegerField()
    pending_swaps = serializers.IntegerField()
    accepted_swaps = serializers.IntegerField()
    completed_swaps = serializers.IntegerField()
    cancelled_swaps = serializers.IntegerField()
    rejected_swaps = serializers.IntegerField()
    
    # Time-based stats
    swaps_this_week = serializers.IntegerField()
    swaps_this_month = serializers.IntegerField()
    swaps_this_year = serializers.IntegerField()
    
    # Average ratings
    average_rating = serializers.FloatField()
    
    # Top skills
    top_offered_skills = serializers.ListField()
    top_wanted_skills = serializers.ListField()

class UserActivityReportSerializer(serializers.Serializer):
    """Serializer for user activity reports"""
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()
    full_name = serializers.CharField()
    join_date = serializers.DateTimeField()
    last_login = serializers.DateTimeField()
    total_swaps = serializers.IntegerField()
    completed_swaps = serializers.IntegerField()
    average_rating = serializers.FloatField()
    reports_received = serializers.IntegerField()
    reports_made = serializers.IntegerField()
    is_banned = serializers.BooleanField()
    ban_reason = serializers.CharField(allow_blank=True)
