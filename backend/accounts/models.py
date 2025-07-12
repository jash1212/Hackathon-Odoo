from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    availability = models.CharField(max_length=50, choices=[
        ('weekdays', 'Weekdays'),
        ('weekends', 'Weekends'),
        ('evenings', 'Evenings'),
        ('mornings', 'Mornings'),
        ('flexible', 'Flexible'),
    ], blank=True)
    experience_level = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner (0-1 years)'),
        ('intermediate', 'Intermediate (2-4 years)'),
        ('advanced', 'Advanced (5+ years)'),
        ('expert', 'Expert (10+ years)'),
    ], blank=True)
    response_time = models.CharField(max_length=100, choices=[
        ('1hour', 'Usually responds within 1 hour'),
        ('3hours', 'Usually responds within 3 hours'),
        ('24hours', 'Usually responds within 24 hours'),
        ('2-3days', 'Usually responds within 2-3 days'),
    ], blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    completed_swaps = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin-related fields
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True)
    ban_date = models.DateTimeField(null=True, blank=True)
    banned_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='bans_given')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

class PlatformMessage(models.Model):
    """Model for platform-wide messages sent by admins"""
    MESSAGE_TYPE_CHOICES = [
        ('announcement', 'Announcement'),
        ('feature_update', 'Feature Update'),
        ('downtime_alert', 'Downtime Alert'),
        ('maintenance', 'Maintenance Notice'),
        ('general', 'General Message'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='general')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.message_type}"

class UserReport(models.Model):
    """Model for user reports and feedback"""
    REPORT_TYPE_CHOICES = [
        ('inappropriate_content', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('fake_profile', 'Fake Profile'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    description = models.TextField()
    evidence = models.TextField(blank=True)  # URLs, screenshots, etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_resolved')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report by {self.reporter.full_name} on {self.reported_user.full_name}"

class SkillReport(models.Model):
    """Model for reporting inappropriate skill descriptions"""
    REPORT_TYPE_CHOICES = [
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('misleading', 'Misleading Description'),
        ('offensive', 'Offensive Language'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('skill_removed', 'Skill Removed'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_reports_made')
    skill = models.ForeignKey('skills.Skill', on_delete=models.CASCADE, related_name='reports_received')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='skill_reports_resolved')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Skill report by {self.reporter.full_name} on {self.skill.name}"
