from django.urls import path
from . import views

urlpatterns = [
    # Profile management endpoints
    path('profile/', views.UserProfileDetailView.as_view(), name='user_profile_detail'),
    path('profile/me/', views.my_profile, name='my_profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/delete-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    
    # Public profile endpoints
    path('profiles/', views.ProfileListView.as_view(), name='profile_list'),
    path('profiles/stats/', views.profile_stats, name='profile_stats'),
    path('profiles/<str:username>/', views.PublicProfileView.as_view(), name='public_profile'),
    
    # Utility endpoints
    path('check-username/', views.check_username, name='check_username'),
    path('check-email/', views.check_email, name='check_email'),
]
