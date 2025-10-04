from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import ContactInquiry


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    """
    Comprehensive admin interface for managing contact inquiries.
    Features filtering, searching, and bulk actions.
    """
    
    # List Display
    list_display = [
        'id',
        'name_with_status',
        'email_link',
        'inquiry_type_badge',
        'subject_preview',
        'priority_badge',
        'status_badge',
        'assigned_to',
        'created_at_formatted',
        'response_time_display',
    ]
    
    # Filters
    list_filter = [
        'status',
        'priority',
        'inquiry_type',
        'created_at',
        'updated_at',
        'assigned_to',
    ]
    
    # Search
    search_fields = [
        'name',
        'email',
        'subject',
        'message',
        'admin_notes',
        'id',
    ]
    
    # Read-only fields
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'resolved_at',
        'ip_address',
        'user_agent',
        'response_time_display',
        'full_message_display',
    ]
    
    # Fieldsets for detail view
    fieldsets = (
        ('Contact Information', {
            'fields': ('id', 'name', 'email', 'created_at')
        }),
        ('Inquiry Details', {
            'fields': ('inquiry_type', 'subject', 'full_message_display')
        }),
        ('Management', {
            'fields': ('status', 'priority', 'assigned_to', 'admin_notes'),
            'classes': ('wide',)
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('updated_at', 'resolved_at', 'response_time_display'),
            'classes': ('collapse',)
        }),
    )
    
    # Date hierarchy
    date_hierarchy = 'created_at'
    
    # Ordering
    ordering = ['-created_at']
    
    # Items per page
    list_per_page = 25
    
    # Actions
    actions = [
        'mark_as_new',
        'mark_as_in_progress',
        'mark_as_resolved',
        'mark_as_closed',
        'set_priority_high',
        'set_priority_medium',
        'set_priority_low',
    ]
    
    # Custom display methods
    def name_with_status(self, obj):
        """Display name with new indicator"""
        if obj.is_new:
            return format_html('<strong>🆕 {}</strong>', obj.name)
        return obj.name
    name_with_status.short_description = 'Name'
    name_with_status.admin_order_field = 'name'
    
    def email_link(self, obj):
        """Make email clickable"""
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)
    email_link.short_description = 'Email'
    email_link.admin_order_field = 'email'
    
    def inquiry_type_badge(self, obj):
        """Display inquiry type with color badge"""
        colors = {
            'general': '#6c757d',
            'partnership': '#007bff',
            'university': '#28a745',
            'technical': '#dc3545',
            'feedback': '#17a2b8',
            'investor': '#ffc107',
            'press': '#6f42c1',
            'other': '#6c757d',
        }
        color = colors.get(obj.inquiry_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_inquiry_type_display()
        )
    inquiry_type_badge.short_description = 'Type'
    inquiry_type_badge.admin_order_field = 'inquiry_type'
    
    def subject_preview(self, obj):
        """Display truncated subject"""
        max_length = 50
        if len(obj.subject) > max_length:
            return obj.subject[:max_length] + '...'
        return obj.subject
    subject_preview.short_description = 'Subject'
    subject_preview.admin_order_field = 'subject'
    
    def priority_badge(self, obj):
        """Display priority with color badge"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        icons = {
            'low': '⬇️',
            'medium': '➡️',
            'high': '⬆️',
            'urgent': '🔥',
        }
        icon = icons.get(obj.priority, '')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{} {}</span>',
            color,
            icon,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    priority_badge.admin_order_field = 'priority'
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'new': '#007bff',
            'in_progress': '#ffc107',
            'resolved': '#28a745',
            'closed': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def created_at_formatted(self, obj):
        """Display formatted creation date"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_formatted.short_description = 'Submitted'
    created_at_formatted.admin_order_field = 'created_at'
    
    def response_time_display(self, obj):
        """Display response time if resolved"""
        if obj.response_time:
            days = obj.response_time.days
            hours = obj.response_time.seconds // 3600
            if days > 0:
                return f"{days}d {hours}h"
            return f"{hours}h"
        elif obj.status in ['resolved', 'closed']:
            return "N/A"
        else:
            # Calculate time since creation
            time_elapsed = timezone.now() - obj.created_at
            days = time_elapsed.days
            hours = time_elapsed.seconds // 3600
            if days > 0:
                return format_html('<span style="color: red;">Pending {}d {}h</span>', days, hours)
            return format_html('<span style="color: orange;">Pending {}h</span>', hours)
    response_time_display.short_description = 'Response Time'
    
    def full_message_display(self, obj):
        """Display full message in detail view"""
        return format_html('<div style="white-space: pre-wrap; padding: 10px; background: #f5f5f5; border-radius: 5px;">{}</div>', obj.message)
    full_message_display.short_description = 'Message'
    
    # Custom actions
    def mark_as_new(self, request, queryset):
        updated = queryset.update(status='new')
        self.message_user(request, f'{updated} inquiries marked as New.')
    mark_as_new.short_description = "Mark as New"
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} inquiries marked as In Progress.')
    mark_as_in_progress.short_description = "Mark as In Progress"
    
    def mark_as_resolved(self, request, queryset):
        for inquiry in queryset:
            inquiry.status = 'resolved'
            if not inquiry.resolved_at:
                inquiry.resolved_at = timezone.now()
            inquiry.save()
        self.message_user(request, f'{queryset.count()} inquiries marked as Resolved.')
    mark_as_resolved.short_description = "Mark as Resolved"
    
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} inquiries marked as Closed.')
    mark_as_closed.short_description = "Mark as Closed"
    
    def set_priority_high(self, request, queryset):
        updated = queryset.update(priority='high')
        self.message_user(request, f'{updated} inquiries set to High priority.')
    set_priority_high.short_description = "Set Priority: High"
    
    def set_priority_medium(self, request, queryset):
        updated = queryset.update(priority='medium')
        self.message_user(request, f'{updated} inquiries set to Medium priority.')
    set_priority_medium.short_description = "Set Priority: Medium"
    
    def set_priority_low(self, request, queryset):
        updated = queryset.update(priority='low')
        self.message_user(request, f'{updated} inquiries set to Low priority.')
    set_priority_low.short_description = "Set Priority: Low"
    
    # Customize the changelist view
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Add summary statistics
        extra_context['new_count'] = ContactInquiry.objects.filter(status='new').count()
        extra_context['in_progress_count'] = ContactInquiry.objects.filter(status='in_progress').count()
        extra_context['resolved_count'] = ContactInquiry.objects.filter(status='resolved').count()
        return super().changelist_view(request, extra_context=extra_context)

