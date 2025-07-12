from rest_framework import serializers
from .models import SwapRequest, SwapSession, SwapRating
from accounts.serializers import UserProfileSerializer
from skills.serializers import SkillSerializer

class SwapRequestSerializer(serializers.ModelSerializer):
    from_user = UserProfileSerializer(read_only=True)
    to_user = UserProfileSerializer(read_only=True)
    skill_offered = SkillSerializer(read_only=True)
    skill_wanted = SkillSerializer(read_only=True)
    
    class Meta:
        model = SwapRequest
        fields = [
            'id', 'from_user', 'to_user', 'skill_offered', 'skill_wanted',
            'message', 'duration', 'preferred_time', 'status', 'created_at', 'updated_at'
        ]

class SwapRequestCreateSerializer(serializers.ModelSerializer):
    skill_offered_id = serializers.IntegerField()
    skill_wanted_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()
    
    class Meta:
        model = SwapRequest
        fields = [
            'to_user_id', 'skill_offered_id', 'skill_wanted_id',
            'message', 'duration', 'preferred_time'
        ]
    
    def create(self, validated_data):
        validated_data['from_user'] = self.context['request'].user
        to_user_id = validated_data.pop('to_user_id')
        skill_offered_id = validated_data.pop('skill_offered_id')
        skill_wanted_id = validated_data.pop('skill_wanted_id')
        
        from django.contrib.auth import get_user_model
        from skills.models import Skill
        
        User = get_user_model()
        validated_data['to_user'] = User.objects.get(id=to_user_id)
        validated_data['skill_offered'] = Skill.objects.get(id=skill_offered_id)
        validated_data['skill_wanted'] = Skill.objects.get(id=skill_wanted_id)
        
        return super().create(validated_data)

class SwapSessionSerializer(serializers.ModelSerializer):
    swap_request = SwapRequestSerializer(read_only=True)
    
    class Meta:
        model = SwapSession
        fields = ['id', 'swap_request', 'scheduled_date', 'completed', 'notes', 'created_at']

class SwapRatingSerializer(serializers.ModelSerializer):
    from_user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = SwapRating
        fields = ['id', 'from_user', 'rating', 'comment', 'created_at']
