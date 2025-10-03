from django.db import models
from django.contrib.auth.models import User
import uuid


class Notification(models.Model):
    """
    Notification model to store user notifications
    """
    
    NOTIFICATION_TYPES = [
        ('follow', 'New Follower'),
        ('like', 'Post Like'),
        ('comment', 'Post Comment'),
        ('project_invite', 'Project Invitation'),
        ('project_join', 'Project Join Request'),
        ('mention', 'Mention'),
        ('announcement', 'Announcement'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Optional reference to related objects
    post_id = models.UUIDField(null=True, blank=True)
    project_id = models.UUIDField(null=True, blank=True)
    comment_id = models.UUIDField(null=True, blank=True)
    
    # Link for notification action
    action_url = models.CharField(max_length=500, blank=True, null=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
    
    @classmethod
    def create_follow_notification(cls, follower, following):
        """Create a notification when someone follows a user"""
        return cls.objects.create(
            recipient=following,
            sender=follower,
            notification_type='follow',
            title='New Follower',
            message=f'{follower.get_full_name() or follower.username} started following you',
            action_url=f'/profile/{follower.username}'
        )
    
    @classmethod
    def create_like_notification(cls, liker, post_author, post_id):
        """Create a notification when someone likes a post"""
        return cls.objects.create(
            recipient=post_author,
            sender=liker,
            notification_type='like',
            title='New Like',
            message=f'{liker.get_full_name() or liker.username} liked your post',
            post_id=post_id,
            action_url=f'/posts/{post_id}'
        )
    
    @classmethod
    def create_comment_notification(cls, commenter, post_author, post_id, comment_id):
        """Create a notification when someone comments on a post"""
        return cls.objects.create(
            recipient=post_author,
            sender=commenter,
            notification_type='comment',
            title='New Comment',
            message=f'{commenter.get_full_name() or commenter.username} commented on your post',
            post_id=post_id,
            comment_id=comment_id,
            action_url=f'/posts/{post_id}'
        )
    
    @classmethod
    def create_project_invite_notification(cls, inviter, invitee, project_id, project_title):
        """Create a notification when someone invites a user to a project"""
        return cls.objects.create(
            recipient=invitee,
            sender=inviter,
            notification_type='project_invite',
            title='Project Invitation',
            message=f'{inviter.get_full_name() or inviter.username} invited you to join {project_title}',
            project_id=project_id,
            action_url=f'/projects/{project_id}'
        )
