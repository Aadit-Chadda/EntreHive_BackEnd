from rest_framework import serializers
from django.contrib.auth.models import User
from posts.models import Post
from projects.models import Project
from posts.serializers import PostListSerializer
from projects.serializers import ProjectSerializer
from .models import ContentScore, UserInteraction, FeedConfiguration, TrendingTopic


class TimelineItemSerializer(serializers.Serializer):
    """
    Serializer for timeline items (replaces FeedItemSerializer)
    Works with dynamically generated timeline data
    """
    content_type = serializers.CharField()
    content_id = serializers.UUIDField()
    score = serializers.FloatField()
    content = serializers.SerializerMethodField()
    user_interactions = serializers.ListField(child=serializers.CharField(), read_only=True)
    viewed = serializers.BooleanField(read_only=True)
    clicked = serializers.BooleanField(read_only=True)
    liked = serializers.BooleanField(read_only=True)
    
    def get_content(self, obj):
        """Get the serialized content object"""
        # Handle both dictionary and object formats for compatibility
        if isinstance(obj, dict):
            content_obj = obj.get('content')
        else:
            content_obj = getattr(obj, 'content', None)
            
        if not content_obj:
            return None
            
        # Get content_type from obj
        content_type = obj.get('content_type') if isinstance(obj, dict) else getattr(obj, 'content_type', None)
            
        if content_type == 'post':
            return PostListSerializer(content_obj, context=self.context).data
        elif content_type == 'project':
            return ProjectSerializer(content_obj, context=self.context).data
        
        return None


class TimelineFeedSerializer(serializers.Serializer):
    """
    Serializer for timeline feed response
    """
    results = TimelineItemSerializer(many=True)
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)


class FeedConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for user feed configuration
    """
    
    class Meta:
        model = FeedConfiguration
        fields = [
            'show_university_posts', 'show_public_posts', 'show_project_updates',
            'preferred_post_types', 'recency_weight', 'relevance_weight',
            'engagement_weight', 'university_weight'
        ]
    
    def validate(self, data):
        """Ensure weights sum to approximately 1.0"""
        weights = [
            data.get('recency_weight', 0.4),
            data.get('relevance_weight', 0.3),
            data.get('engagement_weight', 0.2),
            data.get('university_weight', 0.1)
        ]
        total = sum(weights)
        if abs(total - 1.0) > 0.1:  # Allow some tolerance
            raise serializers.ValidationError(
                "Algorithm weights should sum to approximately 1.0"
            )
        return data


class TrendingTopicSerializer(serializers.ModelSerializer):
    """
    Serializer for trending topics
    """
    universities = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = TrendingTopic
        fields = [
            'topic', 'mention_count', 'universities', 
            'created_at', 'updated_at'
        ]


class UserInteractionSerializer(serializers.ModelSerializer):
    """
    Serializer for tracking user interactions with content
    """
    
    class Meta:
        model = UserInteraction
        fields = [
            'content_type', 'content_id', 'action', 
            'view_time', 'feed_type', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def validate(self, data):
        """Validate that content exists and is accessible"""
        content_type = data.get('content_type')
        content_id = data.get('content_id')
        
        if content_type == 'post':
            try:
                Post.objects.get(id=content_id)
            except Post.DoesNotExist:
                raise serializers.ValidationError("Post not found")
        elif content_type == 'project':
            try:
                Project.objects.get(id=content_id)
            except Project.DoesNotExist:
                raise serializers.ValidationError("Project not found")
        
        return data


class ContentScoreSerializer(serializers.ModelSerializer):
    """
    Serializer for content scores (for admin/analytics)
    """
    
    class Meta:
        model = ContentScore
        fields = [
            'content_type', 'content_id', 'base_score', 
            'engagement_score', 'recency_score', 'trending_score',
            'calculated_at', 'expires_at'
        ]
