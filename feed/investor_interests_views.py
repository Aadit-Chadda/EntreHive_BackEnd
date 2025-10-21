from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.models import UserProfile


def is_investor(user):
    """Check if user has investor role"""
    return hasattr(user, 'profile') and user.profile.user_role == 'investor'


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def investor_interests(request):
    """
    Get or update investor interests
    GET/PUT /api/feed/investor/interests/
    
    GET returns:
    {
        "interests": ["AI", "Fintech", "EdTech"]
    }
    
    PUT expects:
    {
        "interests": ["AI", "Fintech", "EdTech"]
    }
    """
    # Check if user is investor
    if not is_investor(request.user):
        return Response(
            {'error': 'Access denied. This feature is only available to investors.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    profile = request.user.profile
    
    if request.method == 'GET':
        return Response({
            'interests': profile.interests if profile.interests else []
        })
    
    elif request.method == 'PUT':
        interests = request.data.get('interests', [])
        
        # Validate interests
        if not isinstance(interests, list):
            return Response(
                {'error': 'Interests must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate each interest
        valid_topics = [
            'AI', 'Web Dev', 'Fintech', 'Robotics', 'Biotech', 
            'Climate', 'Hardware', 'SaaS', 'EdTech', 'HealthTech', 
            'Social Impact', 'Gaming'
        ]
        
        for interest in interests:
            if not isinstance(interest, str):
                return Response(
                    {'error': 'Each interest must be a string'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if interest not in valid_topics:
                return Response(
                    {'error': f'Invalid interest: {interest}. Must be one of: {", ".join(valid_topics)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Update interests
        profile.interests = interests
        profile.save()
        
        return Response({
            'interests': profile.interests,
            'message': 'Interests updated successfully'
        })

