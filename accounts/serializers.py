from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom registration serializer that requires both username and email
    """
    username = serializers.CharField(
        max_length=150,
        min_length=1,
        required=True
    )
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True
    )
    last_name = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True
    )

    def validate_username(self, username):
        """
        Check if username is unique
        """
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        return username

    def validate_email(self, email):
        """
        Check if email is unique
        """
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        return email

    def get_cleaned_data(self):
        """
        Return cleaned data for user creation
        """
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        }

    def save(self, request):
        """
        Create and return a new user instance
        """
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        return user


# Import this here to avoid circular imports
from allauth.account import app_settings
from allauth.account.adapter import get_adapter


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model with all fields
    """
    full_name = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    role_specific_info = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'full_name',
            'first_name', 'last_name', 'user_role',
            'profile_picture', 'bio', 'location', 'university',
            'major', 'graduation_year',  # Student fields
            'department', 'research_interests',  # Professor fields
            'investment_focus', 'company',  # Investor fields
            'linkedin_url', 'website_url', 'github_url',
            'is_profile_public', 'show_email',
            'role_specific_info', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def validate_user_role(self, value):
        """Validate user role"""
        valid_roles = ['student', 'professor', 'investor']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of: {', '.join(valid_roles)}")
        return value
    
    def validate_graduation_year(self, value):
        """Validate graduation year"""
        if value is not None:
            import datetime
            current_year = datetime.datetime.now().year
            if value < 1950 or value > current_year + 10:
                raise serializers.ValidationError("Graduation year must be between 1950 and 10 years from now")
        return value


class UserProfileCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating user profiles with role-specific validation
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'user_role',
            'profile_picture', 'bio', 'location', 'university',
            'major', 'graduation_year',  # Student fields
            'department', 'research_interests',  # Professor fields
            'investment_focus', 'company',  # Investor fields
            'linkedin_url', 'website_url', 'github_url',
            'is_profile_public', 'show_email'
        ]
    
    def validate(self, data):
        """Cross-field validation based on user role"""
        user_role = data.get('user_role', self.instance.user_role if self.instance else 'student')
        
        # Helper function to check if a field value exists (either in data or instance)
        def has_value(field_name):
            return (data.get(field_name) or 
                   (self.instance and getattr(self.instance, field_name, None)))
        
        # Role-specific validation
        if user_role == 'student':
            if data.get('major') and not has_value('university'):
                raise serializers.ValidationError("University is required when major is specified")
        
        elif user_role == 'professor':
            if data.get('department') and not has_value('university'):
                raise serializers.ValidationError("University is required when department is specified")
        
        elif user_role == 'investor':
            if data.get('investment_focus') and not has_value('company'):
                raise serializers.ValidationError("Company is recommended when investment focus is specified")
        
        return data


class PublicUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for public user profiles (limited fields based on privacy settings)
    """
    full_name = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.SerializerMethodField()
    role_specific_info = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'full_name',
            'user_role', 'profile_picture', 'bio', 
            'location', 'university',
            'linkedin_url', 'website_url', 'github_url',
            'role_specific_info', 'created_at'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_email(self, obj):
        """Only show email if user allows it"""
        if obj.show_email:
            return obj.user.email
        return None
    
    def get_role_specific_info(self, obj):
        """Return role-specific info for public viewing"""
        info = obj.role_specific_info
        # Filter out sensitive information if needed
        return info


class ExtendedRegisterSerializer(CustomRegisterSerializer):
    """
    Extended registration serializer that includes basic profile fields
    """
    user_role = serializers.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        default='student',
        required=False
    )
    bio = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    location = serializers.CharField(max_length=100, required=False, allow_blank=True)
    university = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    def get_cleaned_data(self):
        """
        Return cleaned data including profile fields
        """
        data = super().get_cleaned_data()
        data.update({
            'user_role': self.validated_data.get('user_role', 'student'),
            'bio': self.validated_data.get('bio', ''),
            'location': self.validated_data.get('location', ''),
            'university': self.validated_data.get('university', ''),
        })
        return data
    
    def save(self, request):
        """
        Create user and update profile with additional fields
        """
        user = super().save(request)
        
        # Update the automatically created profile with additional data
        profile = user.profile
        profile.user_role = self.cleaned_data.get('user_role', 'student')
        profile.bio = self.cleaned_data.get('bio', '')
        profile.location = self.cleaned_data.get('location', '')
        profile.university = self.cleaned_data.get('university', '')
        profile.first_name = self.cleaned_data.get('first_name', '')
        profile.last_name = self.cleaned_data.get('last_name', '')
        profile.save()
        
        return user
