from rest_framework import serializers
from .models import Notification


class SimpleUserSerializer(serializers.Serializer):
    """Simple serializer for user in notifications"""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add profile picture if available
        if hasattr(instance, 'profile') and instance.profile.profile_picture:
            request = self.context.get('request')
            if request:
                data['profile_picture'] = request.build_absolute_uri(instance.profile.profile_picture.url)
            else:
                data['profile_picture'] = instance.profile.profile_picture.url
        else:
            data['profile_picture'] = None
        return data


class NotificationSerializer(serializers.ModelSerializer):
    sender = SimpleUserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'notification_type', 
            'title', 'message', 'post_id', 'project_id', 
            'comment_id', 'action_url', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for notification lists"""
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_full_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 
            'sender_username', 'sender_full_name', 'sender_profile_picture',
            'action_url', 'is_read', 'created_at'
        ]
    
    def get_sender_profile_picture(self, obj):
        if obj.sender and hasattr(obj.sender, 'profile') and obj.sender.profile.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.sender.profile.profile_picture.url)
        return None

