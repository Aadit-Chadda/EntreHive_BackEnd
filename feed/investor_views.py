from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count, Case, When, IntegerField, Value, F
from django.contrib.auth.models import User
from projects.models import Project
from posts.models import Post
from projects.serializers import ProjectSerializer
from posts.serializers import PostSerializer
from functools import reduce
import operator


def is_investor(user):
    """Check if user has investor role"""
    return hasattr(user, 'profile') and user.profile.user_role == 'investor'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def investor_feed(request):
    """
    Investor feed endpoint with topic filtering, university filtering, and search
    GET /api/feed/investor/
    
    Query Parameters:
    - feed_type: 'public' or 'university' (default: 'public')
    - university_id: Filter by university (only for university feed)
    - topics: Comma-separated list of topics (e.g., 'AI,Web Dev,Fintech')
    - search: Search query for title/keywords
    - quick_filter: 'funding', 'prototype', 'hiring'
    - sort: 'best_match', 'recent', 'saved' (default: 'best_match')
    - cursor: Pagination cursor (created_at timestamp)
    - limit: Number of results (default: 12, max: 50)
    """
    
    # Check if user is investor
    if not is_investor(request.user):
        return Response(
            {'error': 'Access denied. This feature is only available to investors.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get query parameters
    feed_type = request.GET.get('feed_type', 'public')
    university_id = request.GET.get('university_id', None)
    topics_str = request.GET.get('topics', '')
    search_query = request.GET.get('search', '')
    quick_filter = request.GET.get('quick_filter', None)
    sort_by = request.GET.get('sort', 'best_match')
    cursor = request.GET.get('cursor', None)
    limit = min(int(request.GET.get('limit', 12)), 50)
    
    # Parse topics
    topics = [t.strip() for t in topics_str.split(',') if t.strip()] if topics_str else []
    
    # Base project query
    project_query = Q(visibility__in=['public', 'university'])
    
    # University filtering
    if feed_type == 'university' and university_id:
        project_query &= Q(university_id=university_id)
    
    # Topic filtering
    if topics:
        topic_queries = [Q(categories__contains=topic) for topic in topics]
        project_query &= reduce(operator.or_, topic_queries)
    
    # Search filtering
    if search_query:
        project_query &= (
            Q(title__icontains=search_query) |
            Q(summary__icontains=search_query) |
            Q(tags__contains=search_query)
        )
    
    # Quick filters
    if quick_filter == 'funding':
        project_query &= Q(needs__contains='funding')
    elif quick_filter == 'prototype':
        project_query &= Q(status='mvp') | Q(status='launched')
    elif quick_filter == 'hiring':
        project_query &= Q(needs__contains='dev') | Q(needs__contains='design') | Q(needs__contains='marketing')
    
    # Get projects
    projects = Project.objects.filter(project_query).select_related(
        'owner', 'owner__profile', 'university'
    ).prefetch_related('team_members', 'team_members__profile')
    
    # Calculate match score for sorting
    if topics:
        # Count how many topics match
        match_cases = [
            When(categories__contains=topic, then=Value(1))
            for topic in topics
        ]
        projects = projects.annotate(
            match_score=Count(
                Case(*match_cases, default=Value(0), output_field=IntegerField())
            )
        )
    else:
        projects = projects.annotate(match_score=Value(0))
    
    # Sorting
    if sort_by == 'best_match' and topics:
        projects = projects.order_by('-match_score', '-created_at')
    elif sort_by == 'recent':
        projects = projects.order_by('-created_at')
    elif sort_by == 'saved':
        # TODO: Implement saved/starred functionality
        projects = projects.order_by('-created_at')
    else:
        projects = projects.order_by('-match_score', '-created_at')
    
    # Cursor pagination
    if cursor:
        projects = projects.filter(created_at__lt=cursor)
    
    # Limit projects (prioritize them in feed)
    project_limit = int(limit * 0.83)  # ~10 out of 12
    projects = projects[:project_limit]
    
    # Base post query (posts with visibility public or university)
    post_query = Q(visibility__in=['public', 'university'])
    
    # University filtering for posts
    if feed_type == 'university' and university_id:
        post_query &= Q(author__profile__university_id=university_id)
    
    # Topic filtering for posts (through tagged projects)
    if topics:
        topic_queries_post = [Q(tagged_projects__categories__contains=topic) for topic in topics]
        post_query &= reduce(operator.or_, topic_queries_post)
    
    # Search filtering for posts
    if search_query:
        post_query &= Q(content__icontains=search_query)
    
    # Get posts
    posts = Post.objects.filter(post_query).select_related(
        'author', 'author__profile', 'university'
    ).prefetch_related('tagged_projects', 'likes')
    
    # Cursor pagination for posts
    if cursor:
        posts = posts.filter(created_at__lt=cursor)
    
    post_limit = limit - len(projects)  # Fill remaining slots with posts
    posts = posts.order_by('-created_at')[:post_limit]
    
    # Serialize data
    project_data = ProjectSerializer(projects, many=True, context={'request': request}).data
    post_data = PostSerializer(posts, many=True, context={'request': request}).data
    
    # Combine and sort by priority (projects first, then posts)
    combined_feed = []
    
    # Add projects with priority marker
    for project in project_data:
        project['item_type'] = 'project'
        project['priority'] = 1
        combined_feed.append(project)
    
    # Add posts with lower priority
    for post in post_data:
        post['item_type'] = 'post'
        post['priority'] = 2
        # Add computed fields
        post['likes_count'] = post.get('likes_count', 0)
        post['comments_count'] = post.get('comments_count', 0)
        combined_feed.append(post)
    
    # Sort by priority, then by date
    combined_feed.sort(key=lambda x: (x['priority'], x.get('created_at', '')), reverse=True)
    
    # Determine next cursor
    next_cursor = None
    if combined_feed:
        last_item = combined_feed[-1]
        next_cursor = last_item.get('created_at')
    
    return Response({
        'results': combined_feed,
        'next_cursor': next_cursor,
        'count': len(combined_feed),
        'has_more': len(combined_feed) == limit
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def investor_topics(request):
    """
    Get available topics for filtering
    GET /api/feed/investor/topics/
    """
    if not is_investor(request.user):
        return Response(
            {'error': 'Access denied. This feature is only available to investors.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Define available topics
    topics = [
        {'id': 'AI', 'label': 'AI', 'icon': '🤖'},
        {'id': 'Web Dev', 'label': 'Web Dev', 'icon': '💻'},
        {'id': 'Fintech', 'label': 'Fintech', 'icon': '💰'},
        {'id': 'Robotics', 'label': 'Robotics', 'icon': '🤖'},
        {'id': 'Biotech', 'label': 'Biotech', 'icon': '🧬'},
        {'id': 'Climate', 'label': 'Climate', 'icon': '🌍'},
        {'id': 'Hardware', 'label': 'Hardware', 'icon': '⚙️'},
        {'id': 'SaaS', 'label': 'SaaS', 'icon': '☁️'},
        {'id': 'EdTech', 'label': 'EdTech', 'icon': '📚'},
        {'id': 'HealthTech', 'label': 'HealthTech', 'icon': '🏥'},
        {'id': 'Social Impact', 'label': 'Social Impact', 'icon': '💝'},
        {'id': 'Gaming', 'label': 'Gaming', 'icon': '🎮'},
    ]
    
    return Response({'topics': topics})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def investor_stats(request):
    """
    Get investor-specific statistics
    GET /api/feed/investor/stats/
    """
    if not is_investor(request.user):
        return Response(
            {'error': 'Access denied. This feature is only available to investors.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get counts
    total_projects = Project.objects.filter(visibility__in=['public', 'university']).count()
    raising_funding = Project.objects.filter(
        visibility__in=['public', 'university'],
        needs__contains='funding'
    ).count()
    prototypes_ready = Project.objects.filter(
        visibility__in=['public', 'university'],
        status__in=['mvp', 'launched']
    ).count()
    
    return Response({
        'total_projects': total_projects,
        'raising_funding': raising_funding,
        'prototypes_ready': prototypes_ready,
    })

