from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from projects.models import Project
import uuid


class Post(models.Model):
    """
    Post model for user posts that can optionally tag projects
    """
    
    # Post visibility choices
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('university', 'University'),
        ('private', 'Private'),
    ]
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='posts',
        help_text="Post author"
    )
    
    # Post content
    content = models.TextField(
        max_length=2000,
        validators=[MinLengthValidator(1)],
        help_text="Post content (1-2000 characters)"
    )
    
    # Optional project tagging
    tagged_projects = models.ManyToManyField(
        Project,
        related_name='posts',
        blank=True,
        help_text="Projects tagged in this post"
    )
    
    # Media attachments
    image = models.ImageField(
        upload_to='post_images/',
        blank=True,
        null=True,
        help_text="Optional image attachment"
    )
    
    # Post metadata
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='public',
        help_text="Post visibility level"
    )
    
    is_edited = models.BooleanField(
        default=False,
        help_text="Whether this post has been edited"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['visibility']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.author.username}: {content_preview}"
    
    def get_likes_count(self):
        """Return the number of likes for this post"""
        return self.likes.count()
    
    def get_comments_count(self):
        """Return the number of comments for this post"""
        return self.comments.count()
    
    def is_liked_by(self, user):
        """Check if a user has liked this post"""
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False
    
    def can_view(self, user):
        """Check if a user can view this post based on visibility settings"""
        if self.visibility == 'public':
            return True
        elif self.visibility == 'private':
            return user == self.author
        elif self.visibility == 'university':
            if user.is_authenticated and hasattr(user, 'profile'):
                return (user == self.author or 
                       user.profile.university == self.author.profile.university)
        return False
    
    def can_edit(self, user):
        """Check if a user can edit this post"""
        return user == self.author
    
    def can_delete(self, user):
        """Check if a user can delete this post"""
        return user == self.author


class Comment(models.Model):
    """
    Comment model for post comments
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Post this comment belongs to"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Comment author"
    )
    content = models.TextField(
        max_length=1000,
        validators=[MinLengthValidator(1)],
        help_text="Comment content (1-1000 characters)"
    )
    
    # Parent comment for nested comments/replies
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent comment for nested replies"
    )
    
    is_edited = models.BooleanField(
        default=False,
        help_text="Whether this comment has been edited"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        content_preview = self.content[:30] + "..." if len(self.content) > 30 else self.content
        return f"{self.author.username} on {self.post}: {content_preview}"
    
    def get_replies_count(self):
        """Return the number of replies to this comment"""
        return self.replies.count()
    
    def can_edit(self, user):
        """Check if a user can edit this comment"""
        return user == self.author
    
    def can_delete(self, user):
        """Check if a user can delete this comment"""
        return user == self.author or user == self.post.author


class Like(models.Model):
    """
    Like model for post likes
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        help_text="Post that is liked"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        help_text="User who liked the post"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        unique_together = ('post', 'user')  # Prevent duplicate likes
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes {self.post}"


class PostShare(models.Model):
    """
    Model to track post shares
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='shares',
        help_text="Post that was shared"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_posts',
        help_text="User who shared the post"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Post Share"
        verbose_name_plural = "Post Shares"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} shared {self.post}"