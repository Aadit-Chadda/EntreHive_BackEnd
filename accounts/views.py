from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import UserProfile, Follow
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
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # Support JSON and file uploads
    
    def get_object(self):
        # Get or create profile for the authenticated user
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        print(f"=== BACKEND DEBUG: UserProfileDetailView.get_object ===")
        print(f"User: {self.request.user}")
        print(f"Profile ID: {profile.id}")
        print(f"Profile created: {created}")
        return profile
    
    def get_serializer_class(self):
        method = self.request.method
        print(f"=== BACKEND DEBUG: UserProfileDetailView.get_serializer_class ===")
        print(f"HTTP Method: {method}")
        if method in ['PUT', 'PATCH']:
            print("Using UserProfileCreateUpdateSerializer")
            return UserProfileCreateUpdateSerializer
        print("Using UserProfileSerializer")
        return UserProfileSerializer
    
    def update(self, request, *args, **kwargs):
        print("=" * 60)
        print("=== BACKEND DEBUG: UserProfileDetailView.update START ===")
        print("=" * 60)
        print(f"Request method: {request.method}")
        print(f"Request content type: {request.content_type}")
        print(f"Request data: {request.data}")
        print(f"Request FILES: {request.FILES}")
        print(f"User: {request.user}")
        
        try:
            result = super().update(request, *args, **kwargs)
            print("=== BACKEND DEBUG: UserProfileDetailView.update SUCCESS ===")
            print(f"Response status: {result.status_code}")
            print(f"Response data: {result.data}")
            return result
        except Exception as e:
            print("=== BACKEND DEBUG: UserProfileDetailView.update ERROR ===")
            print(f"Exception type: {type(e)}")
            print(f"Exception message: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise


class ProfileUpdateView(generics.UpdateAPIView):
    """
    Update user profile with validation
    """
    serializer_class = UserProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # Support JSON and file uploads
    
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    """
    Follow a user by username
    """
    try:
        user_to_follow = get_object_or_404(User, username=username)
        
        # Prevent self-following
        if request.user == user_to_follow:
            return Response(
                {'error': 'You cannot follow yourself'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already following
        follow_relationship, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if created:
            return Response(
                {'message': f'You are now following {username}', 'following': True}, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': f'You are already following {username}', 'following': True}, 
                status=status.HTTP_200_OK
            )
            
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, username):
    """
    Unfollow a user by username
    """
    try:
        user_to_unfollow = get_object_or_404(User, username=username)
        
        try:
            follow_relationship = Follow.objects.get(
                follower=request.user,
                following=user_to_unfollow
            )
            follow_relationship.delete()
            return Response(
                {'message': f'You have unfollowed {username}', 'following': False}, 
                status=status.HTTP_200_OK
            )
        except Follow.DoesNotExist:
            return Response(
                {'message': f'You are not following {username}', 'following': False}, 
                status=status.HTTP_200_OK
            )
            
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def follow_status(request, username):
    """
    Check if the current user is following a specific user
    """
    try:
        user_to_check = get_object_or_404(User, username=username)
        
        if request.user == user_to_check:
            return Response(
                {'following': False, 'message': 'Cannot follow yourself'}, 
                status=status.HTTP_200_OK
            )
        
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user_to_check
        ).exists()
        
        return Response(
            {'following': is_following}, 
            status=status.HTTP_200_OK
        )
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def user_search(request):
    """
    Search for users by username, name, or bio
    """
    search_query = request.GET.get('q', '').strip()
    
    if not search_query:
        return Response(
            {'results': [], 'message': 'Please provide a search query'}, 
            status=status.HTTP_200_OK
        )
    
    # Search only public profiles
    profiles = UserProfile.objects.filter(
        is_profile_public=True
    ).filter(
        Q(user__username__icontains=search_query) |
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query) |
        Q(bio__icontains=search_query)
    ).order_by('-created_at')[:20]  # Limit to 20 results
    
    serializer = PublicUserProfileSerializer(profiles, many=True, context={'request': request})
    return Response(
        {'results': serializer.data, 'count': len(serializer.data)}, 
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def simple_comprehensive_search(request):
    """
    Comprehensive search that uses existing search endpoints
    """
    search_query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    
    if not search_query:
        return Response({
            'users': [],
            'posts': [],
            'projects': [],
            'hashtags': [],
            'message': 'Please provide a search query'
        }, status=status.HTTP_200_OK)
    
    results = {
        'users': [],
        'posts': [],
        'projects': [],
        'hashtags': []
    }
    
    # Search Users
    if search_type in ['all', 'users']:
        try:
            user_profiles = UserProfile.objects.filter(
                is_profile_public=True
            ).filter(
                Q(user__username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(bio__icontains=search_query)
            ).order_by('-created_at')[:10]
            
            user_serializer = PublicUserProfileSerializer(user_profiles, many=True, context={'request': request})
            results['users'] = user_serializer.data
        except Exception as e:
            print(f"User search error: {e}")
            results['users'] = []

    # Search Projects using existing view
    if search_type in ['all', 'projects']:
        try:
            from django.test import RequestFactory
            from projects.views import project_search
            
            factory = RequestFactory()
            project_request = factory.get('/api/projects/search/', {'q': search_query})
            project_request.user = request.user
            
            project_response = project_search(project_request)
            if hasattr(project_response, 'data') and project_response.data:
                results['projects'] = project_response.data.get('results', [])[:10]
        except Exception as e:
            print(f"Project search error: {e}")
            results['projects'] = []

    # Search Posts using existing view
    if search_type in ['all', 'posts']:
        try:
            from django.test import RequestFactory
            from posts.views import post_search
            
            factory = RequestFactory()
            post_request = factory.get('/api/search/', {'q': search_query})
            post_request.user = request.user
            
            post_response = post_search(post_request)
            if hasattr(post_response, 'data') and post_response.data:
                results['posts'] = post_response.data.get('results', [])[:10]
        except Exception as e:
            print(f"Post search error: {e}")
            results['posts'] = []

    # Search Hashtags using existing view
    if search_type in ['all', 'hashtags']:
        try:
            from django.test import RequestFactory
            from posts.views import hashtag_search
            
            factory = RequestFactory()
            hashtag_request = factory.get('/api/hashtags/search/', {'q': search_query})
            hashtag_request.user = request.user
            
            hashtag_response = hashtag_search(hashtag_request)
            if hasattr(hashtag_response, 'data') and hashtag_response.data:
                results['hashtags'] = hashtag_response.data.get('hashtags', [])[:10]
        except Exception as e:
            print(f"Hashtag search error: {e}")
            results['hashtags'] = []

    return Response({
        **results,
        'total_count': len(results['users']) + len(results['projects']) + len(results['posts']) + len(results['hashtags']),
        'search_query': search_query,
        'search_type': search_type
    }, status=status.HTTP_200_OK)
