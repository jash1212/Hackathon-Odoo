from django.db import models
from django.conf import settings
from skills.models import Skill

class SwapRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    DURATION_CHOICES = [
        ('30min', '30 minutes'),
        ('1hour', '1 hour'),
        ('1.5hours', '1.5 hours'),
        ('2hours', '2 hours'),
        ('flexible', 'Flexible'),
    ]
    
    TIME_CHOICES = [
        ('weekday-morning', 'Weekday Morning'),
        ('weekday-afternoon', 'Weekday Afternoon'),
        ('weekday-evening', 'Weekday Evening'),
        ('weekend-morning', 'Weekend Morning'),
        ('weekend-afternoon', 'Weekend Afternoon'),
        ('weekend-evening', 'Weekend Evening'),
        ('flexible', 'Flexible'),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_requests'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_requests'
    )
    skill_offered = models.ForeignKey(
        Skill, 
        on_delete=models.CASCADE, 
        related_name='offered_in_swaps'
    )
    skill_wanted = models.ForeignKey(
        Skill, 
        on_delete=models.CASCADE, 
        related_name='wanted_in_swaps'
    )
    message = models.TextField()
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    preferred_time = models.CharField(max_length=30, choices=TIME_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.full_name} -> {self.to_user.full_name}: {self.skill_offered.name} for {self.skill_wanted.name}"

class SwapSession(models.Model):
    """Represents an actual skill swap session"""
    swap_request = models.OneToOneField(SwapRequest, on_delete=models.CASCADE)
    scheduled_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Session for {self.swap_request}"

class SwapRating(models.Model):
    """Rating for a completed swap session"""
    swap_session = models.ForeignKey(SwapSession, on_delete=models.CASCADE, related_name='ratings')
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['swap_session', 'from_user']
    
    def __str__(self):
        return f"{self.from_user.full_name} rated {self.rating} stars"
