from django.contrib import admin
from .models import Project, ProjectInvitation


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'project_type', 'status', 'visibility', 'created_at', 'team_count']
    list_filter = ['project_type', 'status', 'visibility', 'created_at']
    search_fields = ['title', 'summary', 'owner__username', 'owner__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['team_members']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'owner', 'project_type', 'status')
        }),
        ('Content', {
            'fields': ('summary', 'preview_image', 'pitch_url', 'repo_url')
        }),
        ('Categorization', {
            'fields': ('needs', 'categories', 'tags')
        }),
        ('Team & Access', {
            'fields': ('team_members', 'visibility')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def team_count(self, obj):
        return obj.get_team_count()
    team_count.short_description = 'Team Size'


@admin.register(ProjectInvitation)
class ProjectInvitationAdmin(admin.ModelAdmin):
    list_display = ['project', 'inviter', 'invitee', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project__title', 'inviter__username', 'invitee__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Invitation Details', {
            'fields': ('id', 'project', 'inviter', 'invitee', 'message')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )