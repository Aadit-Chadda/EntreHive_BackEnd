from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message, ProjectViewRequest, MessagePermission
from accounts.serializers import UserProfileSerializer
from projects.serializers import ProjectSerializer


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages"""
    
    sender = UserProfileSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_id', 'content',
            'read', 'read_at', 'attachment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sender', 'read', 'read_at', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate message sending permissions"""
        request = self.context.get('request')
        conversation_id = data.get('conversation')
        
        if request and conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id.id if hasattr(conversation_id, 'id') else conversation_id)
                
                # Check if user is participant
                if not conversation.is_participant(request.user):
                    raise serializers.ValidationError("You are not a participant in this conversation")
                
                # Check messaging permissions
                other_participant = conversation.get_other_participant(request.user)
                if not MessagePermission.can_message(request.user, other_participant, conversation):
                    raise serializers.ValidationError(
                        "You don't have permission to send messages in this conversation. "
                        "Students can only reply after receiving a message or having their project view request accepted."
                    )
                
            except Conversation.DoesNotExist:
                raise serializers.ValidationError("Conversation not found")
        
        return data
    
    def create(self, validated_data):
        """Create message with sender from request"""
        request = self.context.get('request')
        validated_data['sender'] = request.user
        return super().create(validated_data)


class ConversationListSerializer(serializers.ModelSerializer):
    """Serializer for listing conversations (inbox view)"""
    
    participant_1 = UserProfileSerializer(read_only=True)
    participant_2 = UserProfileSerializer(read_only=True)
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    related_project = ProjectSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participant_1', 'participant_2', 'other_participant',
            'initiated_by', 'related_project', 'status', 'created_at',
            'updated_at', 'last_message_at', 'last_message', 'unread_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_message_at']
    
    def get_other_participant(self, obj):
        """Get the other participant from current user's perspective"""
        request = self.context.get('request')
        if request and request.user:
            other = obj.get_other_participant(request.user)
            return UserProfileSerializer(other).data
        return None
    
    def get_last_message(self, obj):
        """Get the last message in the conversation"""
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'id': str(last_msg.id),
                'content': last_msg.content[:100],  # Preview only
                'sender_id': last_msg.sender.id,
                'created_at': last_msg.created_at,
                'read': last_msg.read
            }
        return None
    
    def get_unread_count(self, obj):
        """Get unread message count for current user"""
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.exclude(sender=request.user).filter(read=False).count()
        return 0


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed conversation view with messages"""
    
    participant_1 = UserProfileSerializer(read_only=True)
    participant_2 = UserProfileSerializer(read_only=True)
    other_participant = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)
    related_project = ProjectSerializer(read_only=True)
    can_send_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participant_1', 'participant_2', 'other_participant',
            'initiated_by', 'related_project', 'status', 'messages',
            'created_at', 'updated_at', 'last_message_at', 'can_send_message'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_message_at']
    
    def get_other_participant(self, obj):
        """Get the other participant from current user's perspective"""
        request = self.context.get('request')
        if request and request.user:
            other = obj.get_other_participant(request.user)
            return UserProfileSerializer(other).data
        return None
    
    def get_can_send_message(self, obj):
        """Check if current user can send messages in this conversation"""
        request = self.context.get('request')
        if request and request.user:
            other = obj.get_other_participant(request.user)
            return MessagePermission.can_message(request.user, other, obj)
        return False


class CreateConversationSerializer(serializers.Serializer):
    """Serializer for creating a new conversation"""
    
    recipient_id = serializers.IntegerField(required=True)
    message = serializers.CharField(max_length=5000, required=True)
    project_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_recipient_id(self, value):
        """Validate recipient exists and is not the sender"""
        request = self.context.get('request')
        
        try:
            recipient = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Recipient not found")
        
        if request.user == recipient:
            raise serializers.ValidationError("Cannot create conversation with yourself")
        
        return value
    
    def validate(self, data):
        """Validate messaging permissions"""
        request = self.context.get('request')
        recipient = User.objects.get(id=data['recipient_id'])
        
        # Check if user has permission to initiate conversation
        if not MessagePermission.can_message(request.user, recipient):
            raise serializers.ValidationError(
                "You don't have permission to message this user. "
                "Students must first send a project view request to professors/investors."
            )
        
        return data
    
    def create(self, validated_data):
        """Create conversation and initial message"""
        request = self.context.get('request')
        recipient = User.objects.get(id=validated_data['recipient_id'])
        
        # Check if conversation already exists
        from django.db.models import Q
        existing_conv = Conversation.objects.filter(
            Q(participant_1=request.user, participant_2=recipient) |
            Q(participant_1=recipient, participant_2=request.user)
        ).first()
        
        if existing_conv:
            # Add message to existing conversation
            message = Message.objects.create(
                conversation=existing_conv,
                sender=request.user,
                content=validated_data['message']
            )
            return existing_conv
        
        # Create new conversation
        conversation = Conversation.objects.create(
            participant_1=request.user,
            participant_2=recipient,
            initiated_by=request.user,
            related_project_id=validated_data.get('project_id')
        )
        
        # Create initial message
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=validated_data['message']
        )
        
        return conversation


class ProjectViewRequestSerializer(serializers.ModelSerializer):
    """Serializer for project view requests"""
    
    requester = UserProfileSerializer(read_only=True)
    recipient = UserProfileSerializer(read_only=True)
    recipient_id = serializers.IntegerField(write_only=True, required=True)
    project = ProjectSerializer(read_only=True)
    project_id = serializers.UUIDField(write_only=True, required=True)
    conversation = ConversationListSerializer(read_only=True)
    
    class Meta:
        model = ProjectViewRequest
        fields = [
            'id', 'project', 'project_id', 'requester', 'recipient',
            'recipient_id', 'message', 'status', 'conversation',
            'created_at', 'updated_at', 'responded_at'
        ]
        read_only_fields = ['id', 'requester', 'status', 'conversation', 'created_at', 'updated_at', 'responded_at']
    
    def validate_recipient_id(self, value):
        """Validate recipient exists and has correct role"""
        try:
            recipient = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Recipient not found")
        
        if not hasattr(recipient, 'profile'):
            raise serializers.ValidationError("Recipient must have a profile")
        
        if recipient.profile.user_role not in ['professor', 'investor']:
            raise serializers.ValidationError("Can only send project view requests to professors or investors")
        
        return value
    
    def validate_project_id(self, value):
        """Validate project exists and user is a member"""
        from projects.models import Project
        request = self.context.get('request')
        
        try:
            project = Project.objects.get(id=value)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found")
        
        if not project.is_team_member(request.user):
            raise serializers.ValidationError("You must be a member of the project to send view requests")
        
        return value
    
    def validate(self, data):
        """Validate requester is a student"""
        request = self.context.get('request')
        
        if not hasattr(request.user, 'profile'):
            raise serializers.ValidationError("User must have a profile")
        
        if request.user.profile.user_role != 'student':
            raise serializers.ValidationError("Only students can send project view requests")
        
        # Check for duplicate request
        from projects.models import Project
        project = Project.objects.get(id=data['project_id'])
        recipient = User.objects.get(id=data['recipient_id'])
        
        existing_request = ProjectViewRequest.objects.filter(
            project=project,
            recipient=recipient,
            status='pending'
        ).exists()
        
        if existing_request:
            raise serializers.ValidationError("You already have a pending request to this user for this project")
        
        return data
    
    def create(self, validated_data):
        """Create project view request"""
        from projects.models import Project
        request = self.context.get('request')
        
        project = Project.objects.get(id=validated_data['project_id'])
        recipient = User.objects.get(id=validated_data['recipient_id'])
        
        return ProjectViewRequest.objects.create(
            project=project,
            requester=request.user,
            recipient=recipient,
            message=validated_data['message']
        )


class ProjectViewRequestResponseSerializer(serializers.Serializer):
    """Serializer for responding to project view requests"""
    
    action = serializers.ChoiceField(choices=['accept', 'decline'], required=True)
    
    def validate_action(self, value):
        """Validate action"""
        if value not in ['accept', 'decline']:
            raise serializers.ValidationError("Action must be 'accept' or 'decline'")
        return value

