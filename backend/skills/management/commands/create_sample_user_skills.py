from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from skills.models import Skill, UserSkill
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample user skills data for testing'

    def handle(self, *args, **options):
        # Get all users and skills
        users = User.objects.all()
        skills = Skill.objects.all()
        
        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return
            
        if not skills.exists():
            self.stdout.write(self.style.ERROR('No skills found. Please run create_sample_skills first.'))
            return

        # Sample user skills data
        sample_user_skills = [
            # User 1 - Programming focused
            {'user_index': 0, 'skill_names': ['Python', 'JavaScript', 'React'], 'skill_types': ['offered', 'offered', 'offered'], 'proficiency': ['advanced', 'intermediate', 'intermediate']},
            
            # User 2 - Design focused
            {'user_index': 1, 'skill_names': ['UI/UX Design', 'Adobe Photoshop', 'Figma'], 'skill_types': ['offered', 'offered', 'offered'], 'proficiency': ['expert', 'advanced', 'intermediate']},
            
            # User 3 - Marketing focused
            {'user_index': 2, 'skill_names': ['Digital Marketing', 'Social Media Marketing', 'Content Writing'], 'skill_types': ['offered', 'offered', 'offered'], 'proficiency': ['advanced', 'intermediate', 'intermediate']},
            
            # User 4 - Mixed skills
            {'user_index': 3, 'skill_names': ['Data Analysis', 'Excel', 'SQL'], 'skill_types': ['offered', 'offered', 'offered'], 'proficiency': ['intermediate', 'advanced', 'beginner']},
            
            # User 5 - Mobile development
            {'user_index': 4, 'skill_names': ['React Native', 'iOS Development', 'Android Development'], 'skill_types': ['offered', 'offered', 'offered'], 'proficiency': ['intermediate', 'beginner', 'intermediate']},
            
            # User 6 - Business skills
            {'user_index': 5, 'skill_names': ['Project Management', 'Business Strategy', 'Leadership'], 'skill_types': ['offered', 'offered', 'offered'], 'proficiency': ['advanced', 'intermediate', 'advanced']},
            
            # User 7 - Creative skills
            {'user_index': 6, 'skill_names': ['Graphic Design', 'Video Editing', 'Photography'], 'skill_types': ['offered', 'offered', 'offered'], 'proficiency': ['intermediate', 'beginner', 'advanced']},
            
            # User 8 - Technical skills
            {'user_index': 7, 'skill_names': ['Machine Learning', 'Docker', 'AWS'], 'skill_types': ['offered', 'offered', 'offered'], 'proficiency': ['beginner', 'intermediate', 'beginner']},
        ]

        # Add wanted skills for some users
        wanted_skills = [
            {'user_index': 0, 'skill_names': ['UI/UX Design', 'Digital Marketing'], 'skill_types': ['wanted', 'wanted'], 'proficiency': ['beginner', 'beginner']},
            {'user_index': 1, 'skill_names': ['Python', 'JavaScript'], 'skill_types': ['wanted', 'wanted'], 'proficiency': ['beginner', 'beginner']},
            {'user_index': 2, 'skill_names': ['Data Analysis', 'Excel'], 'skill_types': ['wanted', 'wanted'], 'proficiency': ['beginner', 'beginner']},
            {'user_index': 3, 'skill_names': ['Digital Marketing', 'Social Media Marketing'], 'skill_types': ['wanted', 'wanted'], 'proficiency': ['beginner', 'beginner']},
            {'user_index': 4, 'skill_names': ['Business Strategy', 'Project Management'], 'skill_types': ['wanted', 'wanted'], 'proficiency': ['beginner', 'beginner']},
        ]

        created_count = 0

        # Create offered skills
        for skill_data in sample_user_skills:
            if skill_data['user_index'] < len(users):
                user = users[skill_data['user_index']]
                
                for i, skill_name in enumerate(skill_data['skill_names']):
                    try:
                        skill = Skill.objects.get(name__icontains=skill_name)
                        
                        # Check if UserSkill already exists
                        user_skill, created = UserSkill.objects.get_or_create(
                            user=user,
                            skill=skill,
                            skill_type=skill_data['skill_types'][i],
                            defaults={
                                'proficiency_level': skill_data['proficiency'][i]
                            }
                        )
                        
                        if created:
                            created_count += 1
                            self.stdout.write(f"Created: {user.full_name} - {skill.name} ({skill_data['skill_types'][i]})")
                        else:
                            self.stdout.write(f"Already exists: {user.full_name} - {skill.name}")
                            
                    except Skill.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Skill '{skill_name}' not found, skipping..."))

        # Create wanted skills
        for skill_data in wanted_skills:
            if skill_data['user_index'] < len(users):
                user = users[skill_data['user_index']]
                
                for i, skill_name in enumerate(skill_data['skill_names']):
                    try:
                        skill = Skill.objects.get(name__icontains=skill_name)
                        
                        # Check if UserSkill already exists
                        user_skill, created = UserSkill.objects.get_or_create(
                            user=user,
                            skill=skill,
                            skill_type=skill_data['skill_types'][i],
                            defaults={
                                'proficiency_level': skill_data['proficiency'][i]
                            }
                        )
                        
                        if created:
                            created_count += 1
                            self.stdout.write(f"Created: {user.full_name} - {skill.name} ({skill_data['skill_types'][i]})")
                        else:
                            self.stdout.write(f"Already exists: {user.full_name} - {skill.name}")
                            
                    except Skill.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Skill '{skill_name}' not found, skipping..."))

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} user skills!')
        ) 