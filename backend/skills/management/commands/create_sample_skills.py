from django.core.management.base import BaseCommand
from skills.models import Skill

class Command(BaseCommand):
    help = 'Create sample skills for the platform'

    def handle(self, *args, **options):
        sample_skills = [
            # Programming
            {"name": "Python Programming", "description": "Learn Python programming language for web development, data science, and automation", "category": "programming"},
            {"name": "JavaScript", "description": "Master JavaScript for frontend and backend web development", "category": "programming"},
            {"name": "React Development", "description": "Build modern web applications with React framework", "category": "programming"},
            {"name": "Mobile Development", "description": "Develop mobile apps for iOS and Android platforms", "category": "mobile"},
            {"name": "Web Development", "description": "Build websites and web applications using modern technologies", "category": "programming"},
            
            # Design
            {"name": "Graphic Design", "description": "Design logos, posters, and visual content", "category": "design"},
            {"name": "UI/UX Design", "description": "Create user interfaces and user experience designs", "category": "design"},
            {"name": "Digital Art", "description": "Create digital artwork using Photoshop, Illustrator, or Procreate", "category": "design"},
            {"name": "Photography", "description": "Learn photography techniques and composition", "category": "design"},
            {"name": "Video Editing", "description": "Edit videos using Premiere Pro, Final Cut, or DaVinci Resolve", "category": "design"},
            
            # Marketing
            {"name": "Digital Marketing", "description": "Learn SEO, social media marketing, and content strategy", "category": "marketing"},
            {"name": "Content Marketing", "description": "Create engaging content for digital platforms", "category": "marketing"},
            {"name": "Social Media Marketing", "description": "Manage social media presence and campaigns", "category": "marketing"},
            {"name": "Email Marketing", "description": "Design and execute email marketing campaigns", "category": "marketing"},
            {"name": "Brand Strategy", "description": "Develop brand identity and marketing strategies", "category": "marketing"},
            
            # Business
            {"name": "Project Management", "description": "Manage projects effectively using Agile and Scrum methodologies", "category": "business"},
            {"name": "Business Strategy", "description": "Develop business strategies and market analysis", "category": "business"},
            {"name": "Financial Planning", "description": "Learn personal and business financial planning", "category": "business"},
            {"name": "Public Speaking", "description": "Improve public speaking and presentation skills", "category": "business"},
            {"name": "Leadership", "description": "Develop leadership and team management skills", "category": "business"},
            
            # Data Science
            {"name": "Data Analysis", "description": "Analyze and visualize data using Python, R, or Excel", "category": "data"},
            {"name": "Machine Learning", "description": "Learn machine learning algorithms and AI applications", "category": "data"},
            {"name": "Data Visualization", "description": "Create compelling data visualizations and dashboards", "category": "data"},
            {"name": "Statistical Analysis", "description": "Apply statistical methods to analyze data", "category": "data"},
            {"name": "Big Data", "description": "Work with large datasets and big data technologies", "category": "data"},
            
            # Other
            {"name": "Spanish Language", "description": "Learn Spanish language for communication and cultural exchange", "category": "other"},
            {"name": "French Language", "description": "Master French language and culture", "category": "other"},
            {"name": "Guitar", "description": "Learn to play acoustic or electric guitar", "category": "other"},
            {"name": "Cooking", "description": "Learn to cook various cuisines and techniques", "category": "other"},
            {"name": "Yoga", "description": "Practice yoga for flexibility, strength, and mindfulness", "category": "other"},
        ]
        
        created_count = 0
        for skill_data in sample_skills:
            skill, created = Skill.objects.get_or_create(
                name=skill_data["name"],
                defaults={
                    "description": skill_data["description"],
                    "category": skill_data["category"]
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"✅ Created skill: {skill.name}")
            else:
                self.stdout.write(f"⏭️  Skill already exists: {skill.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully created {created_count} new skills!")
        ) 