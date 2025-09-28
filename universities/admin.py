from django.contrib import admin
from .models import University


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'short_name', 'city', 'country', 
        'university_type', 'student_count', 'professor_count', 'project_count'
    ]
    list_filter = [
        'university_type', 'country'
    ]
    search_fields = ['name', 'short_name', 'city', 'email_domain']
    readonly_fields = ['id', 'created_at', 'updated_at', 'student_count', 'professor_count', 'project_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_name', 'university_type', 'description')
        }),
        ('Location', {
            'fields': ('city', 'state_province', 'country')
        }),
        ('Contact & Web', {
            'fields': ('website', 'email_domain', 'logo')
        }),
        ('Statistics', {
            'fields': ('student_count', 'professor_count', 'project_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['update_statistics']
    
    def update_statistics(self, request, queryset):
        for university in queryset:
            university.update_statistics()
        self.message_user(request, f'Statistics updated for {queryset.count()} universities.')
    update_statistics.short_description = "Update statistics for selected universities"
