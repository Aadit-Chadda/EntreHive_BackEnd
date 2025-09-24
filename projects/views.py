from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Project, ProjectInvitation
from .serializers import (
    ProjectSerializer, ProjectCreateSerializer, ProjectUpdateSerializer,
    ProjectInvitationSerializer, AddTeamMemberSerializer
)


class ProjectPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    List all projects or create a new project
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ProjectPagination
    
    def get_queryset(self):
        """
        Filter projects based on user permissions and visibility
        """
        user = self.request.user
        queryset = Project.objects.select_related('owner__profile').prefetch_related('team_members__profile')
        
        # Filter by visibility - users can see:
        # 1. Their own projects (any visibility)
        # 2. Projects they're team members of (any visibility)
        # 3. Public projects
        # 4. University projects if they're from same university
        # 5. Cross-university projects
        # Note: Private projects are only visible to owner and team members
        
        visibility_filter = Q(visibility='public') | Q(visibility='cross_university')
        
        # Add university filter if user has university info
        if hasattr(user, 'profile') and user.profile.university:
            visibility_filter |= Q(visibility='university')
        
        # Add user's own projects and projects they're team members of (including private)
        user_projects_filter = Q(owner=user) | Q(team_members=user)
        
        final_filter = visibility_filter | user_projects_filter
        queryset = queryset.filter(final_filter).distinct()
        
        # Apply search filter
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(summary__icontains=search) |
                Q(categories__icontains=search) |
                Q(tags__icontains=search)
            )
        
        # Apply type filter
        project_type = self.request.query_params.get('type', None)
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        
        # Apply status filter
        project_status = self.request.query_params.get('status', None)
        if project_status:
            queryset = queryset.filter(status=project_status)
        
        # Apply visibility filter
        visibility = self.request.query_params.get('visibility', None)
        if visibility:
            queryset = queryset.filter(visibility=visibility)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectSerializer
    
    def perform_create(self, serializer):
        """
        Set the project owner to the current user when creating
        """
        serializer.save(owner=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Override create to return full project data after creation"""
        # Use ProjectCreateSerializer for input validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the project
        self.perform_create(serializer)
        project = serializer.instance
        
        # Return full project data using ProjectSerializer
        output_serializer = ProjectSerializer(project, context={'request': request})
        headers = self.get_success_headers(output_serializer.data)
        
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a project
    """
    queryset = Project.objects.select_related('owner__profile').prefetch_related('team_members__profile')
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectUpdateSerializer
        return ProjectSerializer
    
    def get_object(self):
        """
        Override to check user permissions
        """
        obj = super().get_object()
        user = self.request.user
        
        # Check if user can view this project
        if not self.can_view_project(obj, user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                detail="You don't have permission to view this project. Private projects are only visible to the owner and team members.",
                code=403
            )
        
        return obj
    
    def can_view_project(self, project, user):
        """
        Check if user can view the project based on visibility rules
        """
        # Owner and team members can always view
        if project.is_team_member(user):
            return True
        
        # Private projects are only visible to owner and team members
        if project.visibility == 'private':
            return False  # Already handled by is_team_member check above
        
        # Public projects are viewable by everyone
        if project.visibility == 'public':
            return True
        
        # Cross-university projects are viewable by all authenticated users
        if project.visibility == 'cross_university':
            return True
        
        # University projects are viewable by users from same university
        if project.visibility == 'university':
            if hasattr(user, 'profile') and hasattr(project.owner, 'profile'):
                return user.profile.university == project.owner.profile.university
        
        return False
    
    def perform_update(self, serializer):
        """
        Only project owner can update
        """
        project = self.get_object()
        if self.request.user != project.owner:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only project owner can update the project.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Only project owner can delete
        """
        if self.request.user != instance.owner:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only project owner can delete the project.")
        
        instance.delete()


class UserProjectsView(generics.ListAPIView):
    """
    List projects for a specific user
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ProjectPagination
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        target_user = get_object_or_404(User, id=user_id)
        current_user = self.request.user
        
        # Base filter: projects where target user is owner or team member
        queryset = Project.objects.select_related('owner__profile').prefetch_related('team_members__profile').filter(
            Q(owner=target_user) | Q(team_members=target_user)
        ).distinct()
        
        # Apply visibility filters - current user can only see:
        # 1. Their own projects (any visibility)
        # 2. Projects they're team members of (any visibility) 
        # 3. Public projects
        # 4. University projects (if same university)
        # 5. Cross-university projects
        # Note: Private projects are only visible to owner and team members
        
        if current_user != target_user:
            # Filter out private projects unless current user is a team member
            visibility_filter = Q(visibility='public') | Q(visibility='cross_university')
            
            # Add university filter if users are from same university
            if (hasattr(current_user, 'profile') and hasattr(target_user, 'profile') and 
                current_user.profile.university == target_user.profile.university):
                visibility_filter |= Q(visibility='university')
            
            # Add projects where current user is owner or team member (including private)
            user_projects_filter = Q(owner=current_user) | Q(team_members=current_user)
            
            final_filter = visibility_filter | user_projects_filter
            queryset = queryset.filter(final_filter)
        
        return queryset.order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_team_member(request, project_id):
    """
    Add a team member to a project by username
    """
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {'error': 'Project not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user can add team members (owner or existing team member)
    if not project.is_team_member(request.user):
        return Response(
            {'error': 'You don\'t have permission to add team members to this project'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = AddTeamMemberSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save(project)
            return Response(
                {
                    'message': f'Successfully added {user.username} to the project',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'full_name': user.profile.get_full_name() if hasattr(user, 'profile') else f"{user.first_name} {user.last_name}".strip()
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_team_member(request, project_id, user_id):
    """
    Remove a team member from a project
    """
    try:
        project = Project.objects.get(id=project_id)
        user_to_remove = User.objects.get(id=user_id)
    except (Project.DoesNotExist, User.DoesNotExist):
        return Response(
            {'error': 'Project or user not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions: owner can remove anyone, users can remove themselves
    if request.user != project.owner and request.user != user_to_remove:
        return Response(
            {'error': 'You don\'t have permission to remove this team member'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Cannot remove the owner
    if user_to_remove == project.owner:
        return Response(
            {'error': 'Cannot remove project owner'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    success = project.remove_team_member(user_to_remove)
    if success:
        return Response(
            {'message': f'Successfully removed {user_to_remove.username} from the project'},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'error': 'User is not a team member of this project'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ProjectInvitationListCreateView(generics.ListCreateAPIView):
    """
    List invitations for a project or create new invitation
    """
    serializer_class = ProjectInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return ProjectInvitation.objects.filter(project_id=project_id).order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project_id'] = self.kwargs.get('project_id')
        return context


class UserInvitationsView(generics.ListAPIView):
    """
    List invitations received by the current user
    """
    serializer_class = ProjectInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProjectInvitation.objects.filter(
            invitee=self.request.user,
            status='pending'
        ).order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def respond_to_invitation(request, invitation_id):
    """
    Accept or decline an invitation
    """
    try:
        invitation = ProjectInvitation.objects.get(id=invitation_id)
    except ProjectInvitation.DoesNotExist:
        return Response(
            {'error': 'Invitation not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user is the invitee
    if request.user != invitation.invitee:
        return Response(
            {'error': 'You don\'t have permission to respond to this invitation'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    action = request.data.get('action')
    if action == 'accept':
        success = invitation.accept()
        if success:
            return Response(
                {'message': 'Invitation accepted successfully'},
                status=status.HTTP_200_OK
            )
    elif action == 'decline':
        success = invitation.decline()
        if success:
            return Response(
                {'message': 'Invitation declined'},
                status=status.HTTP_200_OK
            )
    
    return Response(
        {'error': 'Invalid action or invitation cannot be processed'},
        status=status.HTTP_400_BAD_REQUEST
    )