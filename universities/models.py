from django.db import models
import uuid


class University(models.Model):
    """
    University model to manage institutions and their settings
    """
    
    # University types
    UNIVERSITY_TYPE_CHOICES = [
        ('public', 'Public University'),
        ('private', 'Private University'),
        ('community', 'Community College'),
        ('technical', 'Technical Institute'),
        ('other', 'Other'),
    ]
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=200, 
        unique=True,
        help_text="Official university name"
    )
    short_name = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Common abbreviation (e.g., MIT, UCLA)"
    )
    
    # University details
    university_type = models.CharField(
        max_length=20,
        choices=UNIVERSITY_TYPE_CHOICES,
        default='public',
        help_text="Type of institution"
    )
    
    # Location information
    city = models.CharField(max_length=100, help_text="City where university is located")
    state_province = models.CharField(max_length=100, help_text="State/Province")
    country = models.CharField(max_length=100, help_text="Country")
    
    # Contact and web presence
    website = models.URLField(blank=True, null=True, help_text="Official website")
    email_domain = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Email domain for verification (e.g., mit.edu)"
    )
    
    # University branding
    logo = models.ImageField(
        upload_to='university_logos/', 
        blank=True, 
        null=True,
        help_text="University logo"
    )
    description = models.TextField(
        max_length=1000, 
        blank=True, 
        null=True,
        help_text="Brief description of the university"
    )
    
    
    # Statistics (computed fields)
    student_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of students from this university (auto-updated)"
    )
    professor_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of professors from this university (auto-updated)"
    )
    project_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of projects from this university (auto-updated)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "University"
        verbose_name_plural = "Universities"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country', 'state_province']),
            models.Index(fields=['email_domain']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.city}, {self.country})"
    
    def get_full_location(self):
        """Return formatted location string"""
        return f"{self.city}, {self.state_province}, {self.country}"
    
    def get_display_name(self):
        """Return display name with short name if available"""
        if self.short_name:
            return f"{self.name} ({self.short_name})"
        return self.name
    
    def update_statistics(self):
        """Update computed statistics"""
        from django.contrib.auth.models import User
        from projects.models import Project
        
        # Update user counts
        university_users = User.objects.filter(profile__university=self)
        self.student_count = university_users.filter(profile__user_role='student').count()
        self.professor_count = university_users.filter(profile__user_role='professor').count()
        
        # Update project count
        self.project_count = Project.objects.filter(
            owner__profile__university=self,
            visibility__in=['university', 'public']
        ).count()
        
        self.save()
