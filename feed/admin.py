from django.contrib import admin
from .models import (
    ContentScore, UserInteraction, FeedConfiguration, 
    TrendingTopic, TimelineFeedCache
)


@admin.register(ContentScore)
class ContentScoreAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'content_id', 'base_score', 'engagement_score', 'calculated_at', 'expires_at']
    list_filter = ['content_type', 'calculated_at', 'expires_at']
    search_fields = ['content_id']
    readonly_fields = ['calculated_at']
    ordering = ['-base_score']


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'content_id', 'action', 'feed_type', 'created_at']
    list_filter = ['content_type', 'action', 'feed_type', 'created_at']
    search_fields = ['user__username', 'content_id']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(FeedConfiguration)
class FeedConfigurationAdmin(admin.ModelAdmin):
    list_display = ['user', 'show_university_posts', 'show_public_posts', 'show_project_updates']
    list_filter = ['show_university_posts', 'show_public_posts', 'show_project_updates']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TrendingTopic)
class TrendingTopicAdmin(admin.ModelAdmin):
    list_display = ['topic', 'mention_count', 'last_calculated', 'created_at']
    list_filter = ['last_calculated', 'created_at']
    search_fields = ['topic']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-mention_count']


@admin.register(TimelineFeedCache)
class TimelineFeedCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'feed_type', 'total_count', 'last_refresh', 'expires_at']
    list_filter = ['feed_type', 'last_refresh', 'expires_at']
    search_fields = ['user__username']
    readonly_fields = ['last_refresh']