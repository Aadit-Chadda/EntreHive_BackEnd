from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimelineFeedViewSet, FeedConfigurationViewSet, TrendingTopicViewSet

# Create router for the feed app
router = DefaultRouter()
router.register(r'feed-config', FeedConfigurationViewSet, basename='feed-config')
router.register(r'trending', TrendingTopicViewSet, basename='trending')

urlpatterns = [
    path('', include(router.urls)),
    # Timeline feed endpoints (new scalable system)
    path('timeline/home/', TimelineFeedViewSet.as_view({'get': 'home'}), name='timeline-home'),
    path('timeline/university/', TimelineFeedViewSet.as_view({'get': 'university'}), name='timeline-university'),
    path('timeline/public/', TimelineFeedViewSet.as_view({'get': 'public'}), name='timeline-public'),
    path('timeline/track_interaction/', TimelineFeedViewSet.as_view({'post': 'track_interaction'}), name='timeline-track'),
    
    # Backward compatibility (can be removed after frontend migration)
    path('feed/home/', TimelineFeedViewSet.as_view({'get': 'home'}), name='feed-home'),
    path('feed/university/', TimelineFeedViewSet.as_view({'get': 'university'}), name='feed-university'),
    path('feed/public/', TimelineFeedViewSet.as_view({'get': 'public'}), name='feed-public'),
    path('feed/track_interaction/', TimelineFeedViewSet.as_view({'post': 'track_interaction'}), name='feed-track'),
]
