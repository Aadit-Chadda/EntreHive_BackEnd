from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import uuid


class ContentScore(models.Model):
    """
    Lightweight model to cache base scores for content items
    Eliminates need for per-user feed items
    """
    
    CONTENT_TYPE_CHOICES = [
        ('post', 'Post'),
        ('project', 'Project'),
        ('university_announcement', 'University Announcement'),
    ]
    
    # Content reference
    content_type = models.CharField(
        max_length=30,
        choices=CONTENT_TYPE_CHOICES,
        help_text="Type of content"
    )
    content_id = models.UUIDField(help_text="ID of the content object")
    
    # Base scores (not user-specific)
    base_score = models.FloatField(
        default=0.0,
        help_text="Base content quality score"
    )
    engagement_score = models.FloatField(
        default=0.0,
        help_text="Engagement-based score (likes, comments, etc.)"
    )
    recency_score = models.FloatField(
        default=0.0,
        help_text="Time-decay score"
    )
    trending_score = models.FloatField(
        default=0.0,
        help_text="Trending/viral score"
    )
    
    # Cache metadata
    calculated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        help_text="When this score cache expires"
    )
    
    class Meta:
        verbose_name = "Content Score"
        verbose_name_plural = "Content Scores"
        unique_together = ('content_type', 'content_id')
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['content_type', '-base_score']),
            models.Index(fields=['-calculated_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.content_type} {self.content_id} (score: {self.base_score:.1f})"
    
    def is_expired(self):
        """Check if score cache is expired"""
        return timezone.now() > self.expires_at
    
    def get_content_object(self):
        """Get the actual content object"""
        if self.content_type == 'post':
            from posts.models import Post
            try:
                return Post.objects.get(id=self.content_id)
            except Post.DoesNotExist:
                return None
        elif self.content_type == 'project':
            from projects.models import Project
            try:
                return Project.objects.get(id=self.content_id)
            except Project.DoesNotExist:
                return None
        return None


class UserInteraction(models.Model):
    """
    Track user interactions with content (replaces FeedItem interaction tracking)
    Much more lightweight - only stores actual interactions
    """
    
    ACTION_CHOICES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('like', 'Like'),
        ('share', 'Share'),
        ('comment', 'Comment'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='content_interactions',
        help_text="User who performed the interaction"
    )
    
    # Content reference
    content_type = models.CharField(
        max_length=30,
        choices=ContentScore.CONTENT_TYPE_CHOICES,
        help_text="Type of content"
    )
    content_id = models.UUIDField(help_text="ID of the content object")
    
    # Interaction details
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="Type of interaction"
    )
    
    # Optional metadata
    view_time = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Time spent viewing (for view actions)"
    )
    
    # Feed context (where the interaction happened)
    feed_type = models.CharField(
        max_length=20,
        choices=[
            ('home', 'Home Feed'),
            ('university', 'University Feed'),
            ('public', 'Public Feed'),
            ('profile', 'Profile View'),
            ('direct', 'Direct View'),
        ],
        null=True,
        blank=True,
        help_text="Context where interaction occurred"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "User Interaction"
        verbose_name_plural = "User Interactions"
        indexes = [
            models.Index(fields=['user', 'content_type', 'content_id']),
            models.Index(fields=['content_type', 'content_id', 'action']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.action} {self.content_type} {self.content_id}"


class FeedConfiguration(models.Model):
    """
    Configuration for user feed preferences and algorithms
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='feed_config',
        help_text="User this configuration belongs to"
    )
    
    # Feed preferences
    show_university_posts = models.BooleanField(
        default=True,
        help_text="Show posts from same university"
    )
    show_public_posts = models.BooleanField(
        default=True,
        help_text="Show public posts from other universities"
    )
    show_project_updates = models.BooleanField(
        default=True,
        help_text="Show project updates and launches"
    )
    
    # Content filtering
    preferred_post_types = models.JSONField(
        default=list,
        blank=True,
        help_text="Preferred types of posts (e.g., ['startup', 'research'])"
    )
    blocked_users = models.ManyToManyField(
        User,
        related_name='blocked_by',
        blank=True,
        help_text="Users whose content should not appear in feed"
    )
    
    # Algorithm weights (0.0 to 1.0)
    recency_weight = models.FloatField(
        default=0.4,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Weight for how recent content is"
    )
    relevance_weight = models.FloatField(
        default=0.3,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Weight for content relevance to user"
    )
    engagement_weight = models.FloatField(
        default=0.2,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Weight for content engagement (likes, comments)"
    )
    university_weight = models.FloatField(
        default=0.1,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Weight for same university content"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Feed Configuration"
        verbose_name_plural = "Feed Configurations"
    
    def __str__(self):
        return f"Feed config for {self.user.username}"


class TrendingTopic(models.Model):
    """
    Model to track trending topics across the platform
    """
    
    topic = models.CharField(
        max_length=100,
        unique=True,
        help_text="Trending topic or hashtag"
    )
    mention_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of mentions in the last 24 hours"
    )
    universities = models.ManyToManyField(
        'universities.University',
        related_name='trending_topics',
        blank=True,
        help_text="Universities where this topic is trending"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_calculated = models.DateTimeField(
        default=timezone.now,
        help_text="When trending score was last calculated"
    )
    
    class Meta:
        verbose_name = "Trending Topic"
        verbose_name_plural = "Trending Topics"
        ordering = ['-mention_count', '-updated_at']
        indexes = [
            models.Index(fields=['mention_count']),
            models.Index(fields=['last_calculated']),
        ]
    
    def __str__(self):
        return f"#{self.topic} ({self.mention_count} mentions)"


class TimelineFeedCache(models.Model):
    """
    Lightweight cache for timeline-based feeds
    Stores only content IDs and metadata, not full feed items
    """
    
    FEED_TYPE_CHOICES = [
        ('home', 'Home Feed'),
        ('university', 'University Feed'),
        ('public', 'Public Feed'),
        ('trending', 'Trending Feed'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='timeline_caches',
        help_text="User this cache belongs to"
    )
    feed_type = models.CharField(
        max_length=20,
        choices=FEED_TYPE_CHOICES,
        help_text="Type of feed cached"
    )
    
    # Lightweight cached data - just content references
    cached_content = models.JSONField(
        default=list,
        help_text="List of {content_type, content_id, score} objects"
    )
    
    # Pagination info
    total_count = models.PositiveIntegerField(
        default=0,
        help_text="Total available items for this feed"
    )
    
    # Cache metadata
    last_refresh = models.DateTimeField(
        auto_now=True,
        help_text="When this cache was last refreshed"
    )
    expires_at = models.DateTimeField(
        help_text="When this cache expires"
    )
    
    class Meta:
        verbose_name = "Timeline Feed Cache"
        verbose_name_plural = "Timeline Feed Caches"
        unique_together = ('user', 'feed_type')
        indexes = [
            models.Index(fields=['user', 'feed_type']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['-last_refresh']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.feed_type} timeline cache"
    
    def is_expired(self):
        """Check if cache is expired"""
        return timezone.now() > self.expires_at
    
    def refresh_cache(self, content_items, expiry_hours=1):
        """Refresh the cache with new content items"""
        # Store minimal data: {content_type, content_id, score}
        self.cached_content = [
            {
                'content_type': item['content_type'],
                'content_id': str(item['content_id']),
                'score': item['score']
            }
            for item in content_items
        ]
        self.total_count = len(content_items)
        self.expires_at = timezone.now() + timedelta(hours=expiry_hours)
        self.save()
    
    def get_page(self, page=1, page_size=20):
        """Get a specific page from cached content"""
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        return self.cached_content[start_idx:end_idx]