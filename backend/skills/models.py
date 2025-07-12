from django.db import models
from django.conf import settings

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=[
        ('programming', 'Programming'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('business', 'Business'),
        ('data', 'Data Science'),
        ('mobile', 'Mobile Development'),
        ('other', 'Other'),
    ])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class UserSkill(models.Model):
    SKILL_TYPE_CHOICES = [
        ('offered', 'Offered'),
        ('wanted', 'Wanted'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    skill_type = models.CharField(max_length=10, choices=SKILL_TYPE_CHOICES)
    proficiency_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'skill', 'skill_type']
        
    def __str__(self):
        return f"{self.user.full_name} - {self.skill.name} ({self.skill_type})"
