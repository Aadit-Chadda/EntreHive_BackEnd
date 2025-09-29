from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeedViewSet, FeedConfigurationViewSet, TrendingTopicViewSet

# Create router for the feed app
router = DefaultRouter()
router.register(r'feed-config', FeedConfigurationViewSet, basename='feed-config')
router.register(r'trending', TrendingTopicViewSet, basename='trending')

urlpatterns = [
    path('', include(router.urls)),
    # Custom feed endpoints
    path('feed/home/', FeedViewSet.as_view({'get': 'home'}), name='feed-home'),
    path('feed/university/', FeedViewSet.as_view({'get': 'university'}), name='feed-university'),
    path('feed/public/', FeedViewSet.as_view({'get': 'public'}), name='feed-public'),
    path('feed/track_interaction/', FeedViewSet.as_view({'post': 'track_interaction'}), name='feed-track'),
]
