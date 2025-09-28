from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UniversityViewSet,
    UniversityListView,
    UniversityDetailView,
    UniversityByCountryView,
    UniversityTypesView,
    verify_email_domain,
    search_universities_by_domain
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'universities', UniversityViewSet, basename='university')

app_name = 'universities'

urlpatterns = [
    # Email verification endpoints (must come before ViewSet routes)
    path('api/universities/verify-email/', verify_email_domain, name='verify-email-domain'),
    path('api/universities/search-by-domain/', search_universities_by_domain, name='search-universities-by-domain'),
    
    # Additional simple views
    path('api/universities/list/', UniversityListView.as_view(), name='university-list'),
    path('api/universities/<uuid:pk>/detail/', UniversityDetailView.as_view(), name='university-detail'),
    path('api/universities/country/<str:country>/', UniversityByCountryView.as_view(), name='universities-by-country'),
    path('api/universities/types/', UniversityTypesView.as_view(), name='university-types'),
    
    # ViewSet routes (includes CRUD operations) - must come last
    path('api/', include(router.urls)),
]
