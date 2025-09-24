from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Project CRUD
    path('', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('<uuid:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    
    # User projects
    path('user/<int:user_id>/', views.UserProjectsView.as_view(), name='user-projects'),
    
    # Team management
    path('<uuid:project_id>/team/add/', views.add_team_member, name='add-team-member'),
    path('<uuid:project_id>/team/remove/<int:user_id>/', views.remove_team_member, name='remove-team-member'),
    
    # Invitations
    path('<uuid:project_id>/invitations/', views.ProjectInvitationListCreateView.as_view(), name='project-invitations'),
    path('invitations/me/', views.UserInvitationsView.as_view(), name='my-invitations'),
    path('invitations/<uuid:invitation_id>/respond/', views.respond_to_invitation, name='respond-invitation'),
]
