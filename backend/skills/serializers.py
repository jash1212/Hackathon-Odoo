from rest_framework import serializers
from .models import Skill, UserSkill

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'description']

class UserSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category', read_only=True)
    
    class Meta:
        model = UserSkill
        fields = ['id', 'skill', 'skill_name', 'skill_category', 'skill_type', 'proficiency_level']

class UserSkillCreateSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = UserSkill
        fields = ['skill_name', 'skill_type', 'proficiency_level']
    
    def create(self, validated_data):
        skill_name = validated_data.pop('skill_name')
        skill, created = Skill.objects.get_or_create(
            name=skill_name,
            defaults={'category': 'other'}
        )
        validated_data['skill'] = skill
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
