from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import uuid


class FeedItem(models.Model):
    """
    Feed item model to represent curated content in user feeds
    """
    
    CONTENT_TYPE_CHOICES = [
        ('post', 'Post'),
        ('project', 'Project'),
        ('university_announcement', 'University Announcement'),
    ]
    
    FEED_TYPE_CHOICES = [
        ('home', 'Home Feed'),
        ('university', 'University Feed'),
        ('public', 'Public Feed'),
        ('trending', 'Trending Feed'),
    ]
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feed_items',
        help_text="User whose feed this item belongs to"
    )
    
    # Content reference (polymorphic)
    content_type = models.CharField(
        max_length=30,
        choices=CONTENT_TYPE_CHOICES,
        help_text="Type of content"
    )
    content_id = models.UUIDField(help_text="ID of the content object")
    
    # Feed categorization
    feed_type = models.CharField(
        max_length=20,
        choices=FEED_TYPE_CHOICES,
        default='home',
        help_text="Which feed this item belongs to"
    )
    
    # Curation data
    score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Relevance score for this item (0-100)"
    )
    
    # User interaction tracking
    viewed = models.BooleanField(default=False, help_text="Whether user has viewed this item")
    view_time = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Time spent viewing this item (in seconds)"
    )
    clicked = models.BooleanField(default=False, help_text="Whether user has clicked this item")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Feed Item"
        verbose_name_plural = "Feed Items"
        ordering = ['-score', '-created_at']
        unique_together = ('user', 'content_type', 'content_id', 'feed_type')
        indexes = [
            models.Index(fields=['user', 'feed_type']),
            models.Index(fields=['score']),
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.content_type} {self.content_id} (score: {self.score})"
    
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
    
    def mark_viewed(self, view_time=None):
        """Mark this feed item as viewed"""
        self.viewed = True
        if view_time:
            self.view_time = view_time
        self.save(update_fields=['viewed', 'view_time'])
    
    def mark_clicked(self):
        """Mark this feed item as clicked"""
        self.clicked = True
        self.save(update_fields=['clicked'])


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


class FeedCache(models.Model):
    """
    Cache model to store pre-computed feeds for performance
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feed_caches',
        help_text="User this cache belongs to"
    )
    feed_type = models.CharField(
        max_length=20,
        choices=FeedItem.FEED_TYPE_CHOICES,
        help_text="Type of feed cached"
    )
    
    # Cached data
    cached_items = models.JSONField(
        default=list,
        help_text="Cached feed item IDs in order"
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
        verbose_name = "Feed Cache"
        verbose_name_plural = "Feed Caches"
        unique_together = ('user', 'feed_type')
        indexes = [
            models.Index(fields=['user', 'feed_type']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.feed_type} cache"
    
    def is_expired(self):
        """Check if cache is expired"""
        return timezone.now() > self.expires_at
    
    def refresh_cache(self, new_items, expiry_hours=1):
        """Refresh the cache with new items"""
        # Convert UUIDs to strings for JSON serialization
        self.cached_items = [str(item) for item in new_items]
        self.expires_at = timezone.now() + timedelta(hours=expiry_hours)
        self.save()