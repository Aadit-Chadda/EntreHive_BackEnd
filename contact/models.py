from django.db import models
from django.core.validators import EmailValidator


class ContactInquiry(models.Model):
    """
    Model to store contact form submissions from users.
    All inquiries are managed through Django admin.
    """
    
    INQUIRY_TYPE_CHOICES = [
        ('general', 'General Inquiry'),
        ('partnership', 'Partnership Opportunity'),
        ('university', 'University Partnership'),
        ('technical', 'Technical Support'),
        ('feedback', 'Feedback & Suggestions'),
        ('investor', 'Investor Relations'),
        ('press', 'Press & Media'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Contact Information
    name = models.CharField(max_length=255, help_text="Full name of the person submitting the inquiry")
    email = models.EmailField(validators=[EmailValidator()], help_text="Email address for response")
    
    # Inquiry Details
    inquiry_type = models.CharField(
        max_length=20,
        choices=INQUIRY_TYPE_CHOICES,
        default='general',
        help_text="Type of inquiry"
    )
    subject = models.CharField(max_length=500, help_text="Subject of the inquiry")
    message = models.TextField(help_text="Detailed message from the user")
    
    # Management Fields
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        help_text="Current status of the inquiry"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the inquiry"
    )
    
    # Admin Notes
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes for staff (not visible to user)"
    )
    assigned_to = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Staff member assigned to handle this inquiry"
    )
    
    # Metadata
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of the submitter"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="Browser user agent string"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the inquiry was submitted")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the inquiry was last updated")
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the inquiry was resolved"
    )
    
    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['inquiry_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_inquiry_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        # Auto-set resolved_at when status changes to resolved
        if self.status == 'resolved' and not self.resolved_at:
            from django.utils import timezone
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_new(self):
        """Check if this is a new inquiry"""
        return self.status == 'new'
    
    @property
    def response_time(self):
        """Calculate response time if resolved"""
        if self.resolved_at:
            return self.resolved_at - self.created_at
        return None

