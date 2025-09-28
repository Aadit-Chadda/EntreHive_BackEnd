from rest_framework import serializers
from .models import University


class UniversitySerializer(serializers.ModelSerializer):
    """
    Serializer for University model with all fields
    """
    student_count = serializers.ReadOnlyField()
    professor_count = serializers.ReadOnlyField()
    project_count = serializers.ReadOnlyField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    
    class Meta:
        model = University
        fields = [
            'id', 'name', 'short_name', 'university_type',
            'city', 'state_province', 'country',
            'website', 'email_domain', 'logo', 'description',
            'student_count', 'professor_count', 'project_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_count', 'professor_count', 'project_count', 'created_at', 'updated_at']


class UniversityListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing universities
    """
    full_location = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = University
        fields = [
            'id', 'name', 'short_name', 'display_name',
            'city', 'state_province', 'country', 'full_location',
            'university_type', 'logo', 'student_count'
        ]
        read_only_fields = ['id', 'student_count']
    
    def get_full_location(self, obj):
        return obj.get_full_location()
    
    def get_display_name(self, obj):
        return obj.get_display_name()


class UniversityCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new universities
    """
    class Meta:
        model = University
        fields = [
            'name', 'short_name', 'university_type',
            'city', 'state_province', 'country',
            'website', 'email_domain', 'logo', 'description'
        ]
    
    def validate_name(self, value):
        """Ensure university name is unique"""
        if University.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A university with this name already exists.")
        return value
    
    def validate_email_domain(self, value):
        """Validate email domain format if provided"""
        if value and not value.startswith('@'):
            # Add @ prefix if not present
            value = '@' + value
        return value


class UniversityStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for university statistics
    """
    full_location = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = University
        fields = [
            'id', 'name', 'short_name', 'display_name', 'full_location',
            'student_count', 'professor_count', 'project_count',
            'updated_at'
        ]
        read_only_fields = ['id', 'student_count', 'professor_count', 'project_count', 'updated_at']
    
    def get_full_location(self, obj):
        return obj.get_full_location()
    
    def get_display_name(self, obj):
        return obj.get_display_name()
