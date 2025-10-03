from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Notification
from .serializers import NotificationSerializer, NotificationListSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        """Return notifications for the current user"""
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('sender', 'sender__profile').order_by('-created_at')
    
    def get_serializer_class(self):
        """Use list serializer for list actions"""
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer
    
    def list(self, request, *args, **kwargs):
        """Get all notifications for current user"""
        queryset = self.get_queryset()
        
        # Filter by read status if specified
        is_read = request.query_params.get('is_read', None)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Limit results
        limit = request.query_params.get('limit', None)
        if limit:
            queryset = queryset[:int(limit)]
        
        serializer = self.get_serializer(queryset, many=True)
        
        # Get unread count
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return Response({
            'notifications': serializer.data,
            'unread_count': unread_count,
            'total_count': self.get_queryset().count()
        })
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a specific notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for current user"""
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        return Response({'status': f'{count} notifications marked as read'})
    
    @action(detail=False, methods=['delete'])
    def delete_all_read(self, request):
        """Delete all read notifications for current user"""
        count, _ = Notification.objects.filter(
            recipient=request.user,
            is_read=True
        ).delete()
        return Response({'status': f'{count} notifications deleted'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_follow_suggestions(request):
    """
    Get user suggestions for following based on:
    - Same university
    - Mutual followers
    - Similar interests (same projects, etc.)
    """
    from django.contrib.auth.models import User
    from accounts.models import Follow
    from accounts.serializers import PublicUserProfileSerializer
    
    current_user = request.user
    
    # Get users already following
    following_ids = Follow.objects.filter(
        follower=current_user
    ).values_list('following_id', flat=True)
    
    # Exclude current user and already following
    exclude_ids = list(following_ids) + [current_user.id]
    
    # Get user's university
    user_university = None
    if hasattr(current_user, 'profile'):
        user_university = current_user.profile.university
    
    # Build suggestions query
    suggestions = User.objects.exclude(id__in=exclude_ids)
    
    # Prioritize same university
    if user_university:
        suggestions = suggestions.filter(
            Q(profile__university=user_university)
        )
    
    # Limit to 5-10 suggestions
    limit = int(request.query_params.get('limit', 5))
    suggestions = suggestions.select_related('profile').order_by('?')[:limit]
    
    # Get the profiles to serialize
    profiles = [user.profile for user in suggestions if hasattr(user, 'profile')]
    
    # Serialize the suggestions
    serializer = PublicUserProfileSerializer(profiles, many=True, context={'request': request})
    
    return Response({
        'suggestions': serializer.data,
        'count': len(serializer.data)
    })
