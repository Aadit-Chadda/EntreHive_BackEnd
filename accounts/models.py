from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended user profile with additional information
    One-to-one relationship with Django User model
    """
    
    # Role choices
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('investor', 'Investor'),
    ]
    
    # One-to-one relationship with User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Basic profile information
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    user_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # Profile details
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True,
        help_text="Upload a profile picture"
    )
    bio = models.TextField(max_length=1000, blank=True, null=True, help_text="Tell us about yourself")
    location = models.CharField(max_length=100, blank=True, null=True, help_text="City, Country")
    university = models.ForeignKey(
        'universities.University',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='users',
        help_text="Your university or institution (optional for investors)"
    )
    
    # Additional relevant information based on role
    # For students
    major = models.CharField(max_length=100, blank=True, null=True, help_text="Field of study (for students)")
    graduation_year = models.IntegerField(blank=True, null=True, help_text="Expected/actual graduation year")
    
    # For professors
    department = models.CharField(max_length=100, blank=True, null=True, help_text="Department (for professors)")
    research_interests = models.TextField(max_length=500, blank=True, null=True, help_text="Research areas of interest")
    
    # For investors
    investment_focus = models.TextField(max_length=500, blank=True, null=True, help_text="Investment focus areas")
    company = models.CharField(max_length=200, blank=True, null=True, help_text="Investment firm or company")
    
    # Social links
    linkedin_url = models.URLField(blank=True, null=True, help_text="LinkedIn profile URL")
    website_url = models.URLField(blank=True, null=True, help_text="Personal website URL")
    github_url = models.URLField(blank=True, null=True, help_text="GitHub profile URL")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Privacy settings
    is_profile_public = models.BooleanField(default=True, help_text="Make profile visible to other users")
    show_email = models.BooleanField(default=False, help_text="Show email to other users")
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        full_name = self.get_full_name()
        return f"{full_name} ({self.user.username}) - {self.get_user_role_display()}"

        
    def get_full_name(self):
        """Return full name or username if names not provided"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.user.username
    
    def get_short_name(self):
        """Return first name or username"""
        return self.first_name or self.user.username
    
    @property
    def role_specific_info(self):
        """Return role-specific information as dict"""
        if self.user_role == 'student':
            return {
                'major': self.major,
                'graduation_year': self.graduation_year,
                'university': self.university.name if self.university else None
            }
        elif self.user_role == 'professor':
            return {
                'department': self.department,
                'research_interests': self.research_interests,
                'university': self.university.name if self.university else None
            }
        elif self.user_role == 'investor':
            return {
                'investment_focus': self.investment_focus,
                'company': self.company
            }
        return {}


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a User is created
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile when User is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
