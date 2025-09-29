from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, LikeViewSet, post_search, hashtag_search

# Main router for posts
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')

# Custom URL patterns for nested resources
urlpatterns = [
    path('', include(router.urls)),
    path('posts/<uuid:post_pk>/comments/', CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='post-comments-list'),
    path('posts/<uuid:post_pk>/comments/<uuid:pk>/', CommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='post-comments-detail'),
    path('posts/<uuid:post_pk>/likes/', LikeViewSet.as_view({
        'get': 'list'
    }), name='post-likes-list'),
    
    # Search endpoints
    path('search/', post_search, name='post-search'),
    path('hashtags/search/', hashtag_search, name='hashtag-search'),
]
