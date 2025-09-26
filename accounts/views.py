from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import UserProfile
from .serializers import (
    UserProfileSerializer, 
    UserProfileCreateUpdateSerializer,
    PublicUserProfileSerializer,
    EnhancedUserProfileSerializer,
    EnhancedPublicUserProfileSerializer
)

User = get_user_model()


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Get or update the authenticated user's profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    # Support both JSON and file uploads
    
    def get_object(self):
        # Get or create profile for the authenticated user
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileCreateUpdateSerializer
        return UserProfileSerializer


class ProfileUpdateView(generics.UpdateAPIView):
    """
    Update user profile with validation
    """
    serializer_class = UserProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]
    # Support both JSON and file uploads
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class PublicProfileView(generics.RetrieveAPIView):
    """
    View public profile by username or user ID with posts and projects
    """
    serializer_class = EnhancedPublicUserProfileSerializer
    permission_classes = [AllowAny]
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'
    
    def get_queryset(self):
        # Only return public profiles
        return UserProfile.objects.filter(is_profile_public=True)


class ProfileListView(generics.ListAPIView):
    """
    List public profiles with search and filtering (enhanced with posts and projects)
    """
    serializer_class = EnhancedPublicUserProfileSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = UserProfile.objects.filter(is_profile_public=True)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(bio__icontains=search) |
                Q(university__icontains=search)
            )
        
        # Filter by role
        role = self.request.query_params.get('role', None)
        if role and role in ['student', 'professor', 'investor']:
            queryset = queryset.filter(user_role=role)
        
        # Filter by university
        university = self.request.query_params.get('university', None)
        if university:
            queryset = queryset.filter(university__icontains=university)
        
        # Filter by location
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset.order_by('-created_at')


@api_view(['GET'])
def check_username(request):
    """
    Check if username is available
    """
    username = request.GET.get('username', '')
    if not username:
        return Response(
            {'error': 'Username parameter is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    is_available = not User.objects.filter(username=username).exists()
    return Response(
        {'available': is_available}, 
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def check_email(request):
    """
    Check if email is available
    """
    email = request.GET.get('email', '')
    if not email:
        return Response(
            {'error': 'Email parameter is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    is_available = not User.objects.filter(email=email).exists()
    return Response(
        {'available': is_available}, 
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    """
    Get authenticated user's complete profile information with posts and projects
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
    
    # Use enhanced serializer that includes posts and projects
    serializer = EnhancedUserProfileSerializer(profile, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def profile_stats(request):
    """
    Get profile statistics (counts by role, etc.)
    """
    stats = {
        'total_public_profiles': UserProfile.objects.filter(is_profile_public=True).count(),
        'students': UserProfile.objects.filter(user_role='student', is_profile_public=True).count(),
        'professors': UserProfile.objects.filter(user_role='professor', is_profile_public=True).count(),
        'investors': UserProfile.objects.filter(user_role='investor', is_profile_public=True).count(),
        'with_pictures': UserProfile.objects.filter(
            is_profile_public=True
        ).exclude(profile_picture='').count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile_picture(request):
    """
    Delete the user's profile picture
    """
    try:
        profile = request.user.profile
        if profile.profile_picture:
            profile.profile_picture.delete()
            profile.save()
            return Response(
                {'message': 'Profile picture deleted successfully'}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'No profile picture to delete'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
