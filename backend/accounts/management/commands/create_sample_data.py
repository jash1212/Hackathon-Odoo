from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from skills.models import Skill, UserSkill
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for the skill swap platform'

    def handle(self, *args, **options):
        # Create sample skills
        skills_data = [
            ('React', 'programming'),
            ('JavaScript', 'programming'),
            ('Python', 'programming'),
            ('Django', 'programming'),
            ('Node.js', 'programming'),
            ('Vue.js', 'programming'),
            ('Angular', 'programming'),
            ('TypeScript', 'programming'),
            ('HTML/CSS', 'programming'),
            ('UI/UX Design', 'design'),
            ('Photoshop', 'design'),
            ('Figma', 'design'),
            ('Graphic Design', 'design'),
            ('Digital Marketing', 'marketing'),
            ('SEO', 'marketing'),
            ('Content Writing', 'marketing'),
            ('Data Science', 'data'),
            ('Machine Learning', 'data'),
            ('Data Analysis', 'data'),
            ('Mobile Development', 'mobile'),
            ('iOS Development', 'mobile'),
            ('Android Development', 'mobile'),
            ('Project Management', 'business'),
            ('Business Strategy', 'business'),
        ]

        # Create skills
        for skill_name, category in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_name,
                defaults={'category': category}
            )
            if created:
                self.stdout.write(f'Created skill: {skill_name}')

        # Create sample users
        sample_users = [
            {
                'email': 'sarah@example.com',
                'username': 'sarah_chen',
                'first_name': 'Sarah',
                'last_name': 'Chen',
                'bio': 'Frontend developer with 5 years of experience. Passionate about creating beautiful and functional user interfaces.',
                'location': 'San Francisco, CA',
                'availability': 'weekends',
                'experience_level': 'advanced',
                'response_time': '3hours',
                'skills_offered': ['React', 'JavaScript', 'UI/UX Design'],
                'skills_wanted': ['Python', 'Data Science', 'Machine Learning']
            },
            {
                'email': 'mike@example.com',
                'username': 'mike_rodriguez',
                'first_name': 'Mike',
                'last_name': 'Rodriguez',
                'bio': 'Data scientist and backend developer. Love working with Python and analyzing complex datasets.',
                'location': 'Austin, TX',
                'availability': 'evenings',
                'experience_level': 'expert',
                'response_time': '1hour',
                'skills_offered': ['Python', 'Django', 'Data Analysis'],
                'skills_wanted': ['React', 'UI/UX Design', 'Mobile Development']
            },
            {
                'email': 'emily@example.com',
                'username': 'emily_johnson',
                'first_name': 'Emily',
                'last_name': 'Johnson',
                'bio': 'Creative designer with expertise in visual design and branding. Always eager to learn new technologies.',
                'location': 'New York, NY',
                'availability': 'flexible',
                'experience_level': 'intermediate',
                'response_time': '24hours',
                'skills_offered': ['Graphic Design', 'Photoshop', 'Figma'],
                'skills_wanted': ['HTML/CSS', 'JavaScript', 'React']
            },
            {
                'email': 'david@example.com',
                'username': 'david_kim',
                'first_name': 'David',
                'last_name': 'Kim',
                'bio': 'Mobile app developer specializing in iOS development. Interested in expanding to web development.',
                'location': 'Seattle, WA',
                'availability': 'weekdays',
                'experience_level': 'advanced',
                'response_time': '3hours',
                'skills_offered': ['Mobile Development', 'iOS Development'],
                'skills_wanted': ['Node.js', 'Django', 'React']
            },
            {
                'email': 'lisa@example.com',
                'username': 'lisa_wang',
                'first_name': 'Lisa',
                'last_name': 'Wang',
                'bio': 'Data scientist with strong background in machine learning and statistics. Looking to learn web development.',
                'location': 'Boston, MA',
                'availability': 'weekends',
                'experience_level': 'expert',
                'response_time': '1hour',
                'skills_offered': ['Data Science', 'Machine Learning', 'Python'],
                'skills_wanted': ['JavaScript', 'React', 'UI/UX Design']
            }
        ]

        for user_data in sample_users:
            skills_offered = user_data.pop('skills_offered')
            skills_wanted = user_data.pop('skills_wanted')
            
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={**user_data, 'password': 'password123'}
            )
            
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {user.full_name}')
                
                # Add skills offered
                for skill_name in skills_offered:
                    try:
                        skill = Skill.objects.get(name=skill_name)
                        UserSkill.objects.get_or_create(
                            user=user,
                            skill=skill,
                            skill_type='offered',
                            defaults={'proficiency_level': random.choice(['intermediate', 'advanced', 'expert'])}
                        )
                    except Skill.DoesNotExist:
                        pass
                
                # Add skills wanted
                for skill_name in skills_wanted:
                    try:
                        skill = Skill.objects.get(name=skill_name)
                        UserSkill.objects.get_or_create(
                            user=user,
                            skill=skill,
                            skill_type='wanted',
                            defaults={'proficiency_level': 'beginner'}
                        )
                    except Skill.DoesNotExist:
                        pass

        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
        self.stdout.write('Sample user credentials:')
        self.stdout.write('Email: sarah@example.com, Password: password123')
        self.stdout.write('Email: mike@example.com, Password: password123')
        self.stdout.write('Email: emily@example.com, Password: password123')
        self.stdout.write('Email: david@example.com, Password: password123')
        self.stdout.write('Email: lisa@example.com, Password: password123')
