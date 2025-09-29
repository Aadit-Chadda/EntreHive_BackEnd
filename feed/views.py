from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, F
from django.utils import timezone
from datetime import timedelta
import random

from .models import FeedItem, FeedConfiguration, TrendingTopic, FeedCache
from .serializers import (
    FeedItemSerializer, FeedConfigurationSerializer,
    TrendingTopicSerializer, FeedInteractionSerializer
)
from posts.models import Post
from projects.models import Project


class FeedPagination(PageNumberPagination):
    """Custom pagination for feed"""
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 50


class FeedViewSet(viewsets.ViewSet):
    """
    ViewSet for curated feed functionality
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = FeedPagination
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paginator = self.pagination_class()
    
    @action(detail=False, methods=['get'])
    def home(self, request):
        """Get personalized home feed with curated content"""
        user = request.user
        feed_items = self._get_curated_feed(user, 'home')
        
        page = self.paginator.paginate_queryset(feed_items, request)
        if page is not None:
            serializer = FeedItemSerializer(page, many=True, context={'request': request})
            return self.paginator.get_paginated_response(serializer.data)
        
        serializer = FeedItemSerializer(feed_items, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def university(self, request):
        """Get university-specific feed"""
        user = request.user
        feed_items = self._get_curated_feed(user, 'university')
        
        page = self.paginator.paginate_queryset(feed_items, request)
        if page is not None:
            serializer = FeedItemSerializer(page, many=True, context={'request': request})
            return self.paginator.get_paginated_response(serializer.data)
        
        serializer = FeedItemSerializer(feed_items, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def public(self, request):
        """Get public feed with posts from all universities"""
        user = request.user
        feed_items = self._get_curated_feed(user, 'public')
        
        page = self.paginator.paginate_queryset(feed_items, request)
        if page is not None:
            serializer = FeedItemSerializer(page, many=True, context={'request': request})
            return self.paginator.get_paginated_response(serializer.data)
        
        serializer = FeedItemSerializer(feed_items, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def track_interaction(self, request):
        """Track user interaction with feed items"""
        try:
            feed_item_id = request.data.get('feed_item_id')
            action = request.data.get('action')
            view_time = request.data.get('view_time')
            
            if not feed_item_id or not action:
                return Response(
                    {'error': 'feed_item_id and action are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                feed_item = FeedItem.objects.get(id=feed_item_id, user=request.user)
            except FeedItem.DoesNotExist:
                return Response(
                    {'error': 'Feed item not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Update feed item based on action
            if action == 'view':
                feed_item.mark_viewed(view_time)
            elif action == 'click':
                feed_item.mark_clicked()
            
            return Response({'message': 'Interaction tracked successfully'})
            
        except Exception as e:
            return Response(
                {'error': f'Failed to track interaction: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_curated_feed(self, user, feed_type):
        """Generate curated feed for user"""
        config, _ = FeedConfiguration.objects.get_or_create(user=user)
        user_university = getattr(user.profile, 'university', None) if hasattr(user, 'profile') else None
        
        # Check cache first
        try:
            feed_cache = FeedCache.objects.get(user=user, feed_type=feed_type)
            if not feed_cache.is_expired():
                cached_item_ids = feed_cache.cached_items
                return FeedItem.objects.filter(
                    id__in=cached_item_ids,
                    user=user
                ).order_by('-score', '-created_at')
        except FeedCache.DoesNotExist:
            pass
        
        # Generate fresh feed
        if feed_type == 'home':
            feed_items = self._generate_home_feed(user, config, user_university)
        elif feed_type == 'university':
            feed_items = self._generate_university_feed(user, config, user_university)
        elif feed_type == 'public':
            feed_items = self._generate_public_feed(user, config)
        else:
            feed_items = []
        
        # Cache the results
        self._cache_feed(user, feed_type, [item.id for item in feed_items])
        return feed_items
    
    def _generate_home_feed(self, user, config, user_university):
        """Generate personalized home feed"""
        FeedItem.objects.filter(user=user, feed_type='home').delete()
        
        content_items = []
        
        # Get university posts if enabled
        if config.show_university_posts and user_university:
            university_posts = Post.objects.filter(
                Q(visibility='university', university=user_university) |
                Q(visibility='public', university=user_university)
            ).exclude(author=user).select_related('author', 'author__profile').annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True)
            )[:20]
            
            for post in university_posts:
                score = self._calculate_post_score(post, user, config, True)
                content_items.append(('post', post, score))
        
        # Get public posts from other universities
        if config.show_public_posts:
            public_posts = Post.objects.filter(
                visibility='public'
            ).exclude(university=user_university).exclude(author=user).select_related(
                'author', 'author__profile'
            ).annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True)
            )[:15]
            
            for post in public_posts:
                score = self._calculate_post_score(post, user, config, False)
                content_items.append(('post', post, score))
        
        # Get relevant projects
        if config.show_project_updates:
            if user_university:
                projects = Project.objects.filter(
                    Q(visibility='university', university=user_university) |
                    Q(visibility='public')
                ).exclude(owner=user).select_related('owner', 'owner__profile')[:10]
            else:
                projects = Project.objects.filter(
                    visibility='public'
                ).exclude(owner=user).select_related('owner', 'owner__profile')[:10]
            
            for project in projects:
                score = self._calculate_project_score(project, user, config, 
                                                   project.university == user_university)
                content_items.append(('project', project, score))
        
        # Sort by score and create feed items
        content_items.sort(key=lambda x: x[2], reverse=True)
        
        feed_items = []
        for content_type, content_obj, score in content_items[:30]:
            feed_item, created = FeedItem.objects.get_or_create(
                user=user,
                content_type=content_type,
                content_id=content_obj.id,
                feed_type='home',
                defaults={'score': score}
            )
            if not created:
                # Update score if item already exists
                feed_item.score = score
                feed_item.save(update_fields=['score'])
            feed_items.append(feed_item)
        
        return feed_items
    
    def _generate_university_feed(self, user, config, user_university):
        """Generate university-specific feed"""
        if not user_university:
            return []
        
        FeedItem.objects.filter(user=user, feed_type='university').delete()
        
        content_items = []
        
        # Get university posts only
        university_posts = Post.objects.filter(
            Q(visibility='university', university=user_university) |
            Q(visibility='public', university=user_university)
        ).select_related('author', 'author__profile').annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )[:30]
        
        for post in university_posts:
            score = self._calculate_post_score(post, user, config, True)
            content_items.append(('post', post, score))
        
        # Get university projects
        university_projects = Project.objects.filter(
            Q(visibility='university', university=user_university) |
            Q(visibility='public', university=user_university)
        ).select_related('owner', 'owner__profile')[:15]
        
        for project in university_projects:
            score = self._calculate_project_score(project, user, config, True)
            content_items.append(('project', project, score))
        
        content_items.sort(key=lambda x: x[2], reverse=True)
        
        feed_items = []
        for content_type, content_obj, score in content_items:
            feed_item, created = FeedItem.objects.get_or_create(
                user=user,
                content_type=content_type,
                content_id=content_obj.id,
                feed_type='university',
                defaults={'score': score}
            )
            if not created:
                # Update score if item already exists
                feed_item.score = score
                feed_item.save(update_fields=['score'])
            feed_items.append(feed_item)
        
        return feed_items
    
    def _generate_public_feed(self, user, config):
        """Generate public feed with content from all universities"""
        FeedItem.objects.filter(user=user, feed_type='public').delete()
        
        content_items = []
        
        # Get public posts
        public_posts = Post.objects.filter(
            visibility='public'
        ).select_related('author', 'author__profile').annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )[:40]
        
        for post in public_posts:
            score = self._calculate_post_score(post, user, config, False)
            content_items.append(('post', post, score))
        
        # Get public projects
        public_projects = Project.objects.filter(
            visibility='public'
        ).select_related('owner', 'owner__profile')[:20]
        
        for project in public_projects:
            score = self._calculate_project_score(project, user, config, False)
            content_items.append(('project', project, score))
        
        content_items.sort(key=lambda x: x[2], reverse=True)
        
        feed_items = []
        for content_type, content_obj, score in content_items:
            feed_item, created = FeedItem.objects.get_or_create(
                user=user,
                content_type=content_type,
                content_id=content_obj.id,
                feed_type='public',
                defaults={'score': score}
            )
            if not created:
                # Update score if item already exists
                feed_item.score = score
                feed_item.save(update_fields=['score'])
            feed_items.append(feed_item)
        
        return feed_items
    
    def _calculate_post_score(self, post, user, config, is_same_university):
        """Calculate relevance score for a post"""
        score = 0.0
        
        # Recency score (0-25 points)
        hours_old = (timezone.now() - post.created_at).total_seconds() / 3600
        recency_score = max(0, 25 - (hours_old / 24) * 25)
        score += recency_score * config.recency_weight * 4
        
        # Engagement score (0-25 points)
        likes_count = getattr(post, 'likes_count', 0)
        comments_count = getattr(post, 'comments_count', 0)
        engagement_score = min(25, (likes_count * 2 + comments_count * 3))
        score += engagement_score * config.engagement_weight * 4
        
        # University bonus (0-25 points)
        university_score = 25 if is_same_university else 5
        score += university_score * config.university_weight * 4
        
        # Relevance score (0-25 points)
        relevance_score = 15  # Base relevance
        score += relevance_score * config.relevance_weight * 4
        
        # Add randomization
        score += random.uniform(-2, 2)
        
        return max(0, min(100, score))
    
    def _calculate_project_score(self, project, user, config, is_same_university):
        """Calculate relevance score for a project"""
        score = 0.0
        
        # Recency score
        hours_old = (timezone.now() - project.created_at).total_seconds() / 3600
        recency_score = max(0, 25 - (hours_old / 24) * 25)
        score += recency_score * config.recency_weight * 4
        
        # Project attractiveness
        attractiveness_score = 15
        if project.needs:
            attractiveness_score += len(project.needs) * 2
        score += min(25, attractiveness_score) * config.engagement_weight * 4
        
        # University bonus
        university_score = 25 if is_same_university else 5
        score += university_score * config.university_weight * 4
        
        # Relevance
        relevance_score = 15
        score += relevance_score * config.relevance_weight * 4
        
        return max(0, min(100, score))
    
    def _cache_feed(self, user, feed_type, item_ids):
        """Cache feed items for performance"""
        try:
            cache = FeedCache.objects.get(user=user, feed_type=feed_type)
            cache.refresh_cache(item_ids, expiry_hours=1)
        except FeedCache.DoesNotExist:
            # Create new cache with proper expires_at value
            cache = FeedCache.objects.create(
                user=user,
                feed_type=feed_type,
                cached_items=[str(item_id) for item_id in item_ids],
                expires_at=timezone.now() + timedelta(hours=1)
            )


class FeedConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet for user feed configuration"""
    serializer_class = FeedConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FeedConfiguration.objects.filter(user=self.request.user)
    
    def get_object(self):
        config, created = FeedConfiguration.objects.get_or_create(user=self.request.user)
        return config
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save()
        FeedCache.objects.filter(user=self.request.user).delete()


class TrendingTopicViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for trending topics"""
    serializer_class = TrendingTopicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = TrendingTopic.objects.all()
    
    def get_queryset(self):
        queryset = TrendingTopic.objects.all()
        university_id = self.request.query_params.get('university')
        if university_id:
            queryset = queryset.filter(universities__id=university_id)
        return queryset.order_by('-mention_count')[:20]