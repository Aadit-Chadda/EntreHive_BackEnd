from django.urls import path
from . import views
from .views_password_reset import custom_password_reset_confirm

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
    
    # Follow endpoints
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('follow-status/<str:username>/', views.follow_status, name='follow_status'),
    
    # Search endpoints
    path('search/users/', views.user_search, name='user_search'),
    path('search/', views.simple_comprehensive_search, name='comprehensive_search'),
    
    # Utility endpoints
    path('check-username/', views.check_username, name='check_username'),
    path('check-email/', views.check_email, name='check_email'),
    
    # Custom password reset confirm endpoint
    path('password-reset-confirm/', custom_password_reset_confirm, name='custom_password_reset_confirm'),
    
    # Email verification endpoints
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification_email'),
]
