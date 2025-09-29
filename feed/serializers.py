from rest_framework import serializers
from django.contrib.auth.models import User
from posts.models import Post
from projects.models import Project
from posts.serializers import PostListSerializer
from projects.serializers import ProjectSerializer
from .models import FeedItem, FeedConfiguration, TrendingTopic


class FeedItemSerializer(serializers.ModelSerializer):
    """
    Serializer for feed items with embedded content
    """
    content = serializers.SerializerMethodField()
    
    class Meta:
        model = FeedItem
        fields = [
            'id', 'content_type', 'content_id', 'feed_type', 
            'score', 'viewed', 'clicked', 'created_at', 'content'
        ]
    
    def get_content(self, obj):
        """Get the serialized content object"""
        content_obj = obj.get_content_object()
        if not content_obj:
            return None
            
        if obj.content_type == 'post':
            return PostListSerializer(content_obj, context=self.context).data
        elif obj.content_type == 'project':
            return ProjectSerializer(content_obj, context=self.context).data
        
        return None


class CuratedFeedSerializer(serializers.Serializer):
    """
    Serializer for curated feed response
    """
    results = FeedItemSerializer(many=True)
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()


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


class FeedInteractionSerializer(serializers.Serializer):
    """
    Serializer for tracking feed interactions
    """
    feed_item_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=['view', 'click', 'like', 'share'])
    view_time = serializers.FloatField(required=False, allow_null=True)
    
    def validate_feed_item_id(self, value):
        """Validate that feed item exists and belongs to the user"""
        user = self.context['request'].user
        try:
            feed_item = FeedItem.objects.get(id=value, user=user)
            return value
        except FeedItem.DoesNotExist:
            raise serializers.ValidationError("Feed item not found or doesn't belong to you")
