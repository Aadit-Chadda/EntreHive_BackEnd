from django.contrib import admin
from .models import Post, Comment, Like, PostShare


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'content_preview', 'visibility', 'is_edited', 'likes_count', 'comments_count', 'created_at']
    list_filter = ['visibility', 'is_edited', 'created_at', 'author__profile__user_role']
    search_fields = ['content', 'author__username', 'author__profile__first_name', 'author__profile__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'likes_count', 'comments_count']
    filter_horizontal = ['tagged_projects']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def likes_count(self, obj):
        return obj.get_likes_count()
    likes_count.short_description = 'Likes'
    
    def comments_count(self, obj):
        return obj.get_comments_count()
    comments_count.short_description = 'Comments'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'content_preview', 'parent', 'is_edited', 'created_at']
    list_filter = ['is_edited', 'created_at', 'post__visibility']
    search_fields = ['content', 'author__username', 'post__content']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['post', 'parent']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:30] + "..." if len(obj.content) > 30 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'created_at']
    list_filter = ['created_at', 'post__visibility']
    search_fields = ['user__username', 'post__content']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['post']
    date_hierarchy = 'created_at'


@admin.register(PostShare)
class PostShareAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'created_at']
    list_filter = ['created_at', 'post__visibility']
    search_fields = ['user__username', 'post__content']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['post']
    date_hierarchy = 'created_at'