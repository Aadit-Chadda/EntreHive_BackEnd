from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, get_follow_suggestions

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notification')

urlpatterns = [
    path('follow-suggestions/', get_follow_suggestions, name='follow-suggestions'),
    path('', include(router.urls)),
]

