"""
Comprehensive search views that coordinate search across all apps
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from django.db.models import Q, Count
import re

from posts.models import Post
from projects.models import Project
from accounts.models import UserProfile
from posts.serializers import PostListSerializer
from projects.serializers import ProjectSerializer
from accounts.serializers import PublicUserProfileSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def comprehensive_search(request):
    """
    Comprehensive search across users, posts, projects, and hashtags
    """
    search_query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')  # all, users, posts, projects, hashtags
    
    if not search_query:
        return Response({
            'users': [],
            'posts': [],
            'projects': [],
            'hashtags': [],
            'message': 'Please provide a search query'
        }, status=status.HTTP_200_OK)
    
    user = request.user
    results = {
        'users': [],
        'posts': [],
        'projects': [],
        'hashtags': []
    }
    
    # Search Users
    if search_type in ['all', 'users']:
        user_profiles = UserProfile.objects.filter(
            is_profile_public=True
        ).filter(
            Q(user__username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(bio__icontains=search_query) |
            Q(university__icontains=search_query)
        ).order_by('-created_at')[:20]
        
        user_serializer = PublicUserProfileSerializer(user_profiles, many=True, context={'request': request})
        results['users'] = user_serializer.data
    
    # Search Posts
    if search_type in ['all', 'posts']:
        post_queryset = Post.objects.select_related('author', 'author__profile').prefetch_related(
            'tagged_projects', 'likes', 'comments'
        ).annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )
        
        # Apply visibility filtering for posts
        if user.is_authenticated:
            user_university = getattr(user.profile, 'university', None) if hasattr(user, 'profile') else None
            post_queryset = post_queryset.filter(
                Q(visibility='public') |
                Q(author=user) |
                (Q(visibility='university') & Q(author__profile__university=user_university) if user_university else Q(pk=None))
            )
        else:
            post_queryset = post_queryset.filter(visibility='public')
        
        # Search posts
        post_search_filters = Q()
        if search_query.startswith('#'):
            hashtag = search_query[1:]
            post_search_filters |= Q(content__icontains=f'#{hashtag}')
        else:
            post_search_filters |= (
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query) |
                Q(author__profile__first_name__icontains=search_query) |
                Q(author__profile__last_name__icontains=search_query) |
                Q(tagged_projects__title__icontains=search_query)
            )
        
        posts = post_queryset.filter(post_search_filters).distinct().order_by('-created_at')[:20]
        post_serializer = PostListSerializer(posts, many=True, context={'request': request})
        results['posts'] = post_serializer.data
    
    # Search Projects
    if search_type in ['all', 'projects']:
        project_queryset = Project.objects.select_related('owner__profile').prefetch_related('team_members__profile')
        
        # Apply visibility filtering for projects
        if user.is_authenticated:
            visibility_filter = Q(visibility='public')
            
            if hasattr(user, 'profile') and user.profile.university:
                visibility_filter |= Q(visibility='university', university=user.profile.university)
            
            user_projects_filter = Q(owner=user) | Q(team_members=user)
            final_filter = visibility_filter | user_projects_filter
            project_queryset = project_queryset.filter(final_filter)
        else:
            project_queryset = project_queryset.filter(visibility='public')
        
        # Search projects
        project_search_filters = (
            Q(title__icontains=search_query) |
            Q(summary__icontains=search_query) |
            Q(categories__icontains=search_query) |
            Q(tags__icontains=search_query) |
            Q(needs__icontains=search_query) |
            Q(owner__username__icontains=search_query) |
            Q(owner__profile__first_name__icontains=search_query) |
            Q(owner__profile__last_name__icontains=search_query)
        )
        
        projects = project_queryset.filter(project_search_filters).distinct().order_by('-created_at')[:20]
        project_serializer = ProjectSerializer(projects, many=True, context={'request': request})
        results['projects'] = project_serializer.data
    
    # Extract Hashtags
    if search_type in ['all', 'hashtags']:
        # Get hashtags from posts that user can see
        post_queryset = Post.objects.select_related('author', 'author__profile')
        
        if user.is_authenticated:
            user_university = getattr(user.profile, 'university', None) if hasattr(user, 'profile') else None
            post_queryset = post_queryset.filter(
                Q(visibility='public') |
                Q(author=user) |
                (Q(visibility='university') & Q(author__profile__university=user_university) if user_university else Q(pk=None))
            )
        else:
            post_queryset = post_queryset.filter(visibility='public')
        
        # Extract hashtags from all accessible posts
        all_hashtags = set()
        for post in post_queryset:
            hashtags_in_content = re.findall(r'#(\w+)', post.content)
            all_hashtags.update(hashtags_in_content)
        
        # Filter hashtags based on search query
        matching_hashtags = [tag for tag in all_hashtags if search_query.lower() in tag.lower()]
        results['hashtags'] = sorted(matching_hashtags, key=lambda x: x.lower())[:20]
    
    # Add counts
    total_count = len(results['users']) + len(results['posts']) + len(results['projects']) + len(results['hashtags'])
    
    return Response({
        **results,
        'total_count': total_count,
        'search_query': search_query,
        'search_type': search_type
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def trending_hashtags(request):
    """
    Get trending hashtags from recent posts
    """
    user = request.user
    
    # Get recent posts (last 30 days or recent 1000 posts)
    post_queryset = Post.objects.select_related('author', 'author__profile')
    
    if user.is_authenticated:
        user_university = getattr(user.profile, 'university', None) if hasattr(user, 'profile') else None
        post_queryset = post_queryset.filter(
            Q(visibility='public') |
            Q(author=user) |
            (Q(visibility='university') & Q(author__profile__university=user_university) if user_university else Q(pk=None))
        )
    else:
        post_queryset = post_queryset.filter(visibility='public')
    
    # Get recent posts and extract hashtags
    recent_posts = post_queryset.order_by('-created_at')[:1000]
    hashtag_counts = {}
    
    for post in recent_posts:
        hashtags = re.findall(r'#(\w+)', post.content)
        for hashtag in hashtags:
            hashtag_lower = hashtag.lower()
            hashtag_counts[hashtag_lower] = hashtag_counts.get(hashtag_lower, 0) + 1
    
    # Sort by frequency and return top trending hashtags
    trending = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    trending_hashtags = [{'hashtag': hashtag, 'count': count} for hashtag, count in trending]
    
    return Response({
        'results': trending_hashtags,
        'count': len(trending_hashtags)
    }, status=status.HTTP_200_OK)
