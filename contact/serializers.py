from rest_framework import serializers
from .models import ContactInquiry


class ContactInquirySerializer(serializers.ModelSerializer):
    """
    Serializer for creating contact inquiries.
    Only used for POST requests from the frontend.
    """
    
    class Meta:
        model = ContactInquiry
        fields = [
            'name',
            'email',
            'inquiry_type',
            'subject',
            'message',
        ]
        extra_kwargs = {
            'name': {'required': True},
            'email': {'required': True},
            'inquiry_type': {'required': True},
            'subject': {'required': True},
            'message': {'required': True},
        }
    
    def validate_message(self, value):
        """Ensure message is not too short"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value
    
    def validate_subject(self, value):
        """Ensure subject is not too short"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Subject must be at least 5 characters long.")
        return value
    
    def create(self, validated_data):
        """Create a new contact inquiry with default status and priority"""
        # Get IP address and user agent from request context if available
        request = self.context.get('request')
        if request:
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            validated_data['ip_address'] = ip_address
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        # Set default status and priority
        validated_data['status'] = 'new'
        
        # Auto-assign priority based on inquiry type
        inquiry_type = validated_data.get('inquiry_type')
        if inquiry_type in ['technical', 'urgent']:
            validated_data['priority'] = 'high'
        elif inquiry_type in ['partnership', 'university', 'investor']:
            validated_data['priority'] = 'medium'
        else:
            validated_data['priority'] = 'low'
        
        return super().create(validated_data)

