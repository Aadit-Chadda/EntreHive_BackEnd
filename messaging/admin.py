from django.contrib import admin
from .models import Conversation, Message, ProjectViewRequest, MessagePermission


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'participant_1', 'participant_2', 'initiated_by', 'status', 'last_message_at', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['participant_1__username', 'participant_2__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_message_at']
    raw_id_fields = ['participant_1', 'participant_2', 'initiated_by', 'related_project']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation', 'read', 'created_at']
    list_filter = ['read', 'created_at']
    search_fields = ['sender__username', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at', 'read_at']
    raw_id_fields = ['conversation', 'sender']


@admin.register(ProjectViewRequest)
class ProjectViewRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'requester', 'recipient', 'project', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['requester__username', 'recipient__username', 'project__title']
    readonly_fields = ['id', 'created_at', 'updated_at', 'responded_at']
    raw_id_fields = ['project', 'requester', 'recipient', 'conversation']


@admin.register(MessagePermission)
class MessagePermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_user', 'to_user', 'grant_type', 'created_at']
    list_filter = ['grant_type', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['from_user', 'to_user', 'conversation']
