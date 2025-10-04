from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import ContactInquiry
from .serializers import ContactInquirySerializer
from django.core.mail import send_mail
from django.conf import settings


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow unauthenticated users to submit
def create_contact_inquiry(request):
    """
    Create a new contact inquiry.
    
    POST /api/contact/
    
    Request body:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "inquiry_type": "general",
        "subject": "Question about services",
        "message": "I would like to know more about..."
    }
    
    Returns:
    - 201: Inquiry created successfully
    - 400: Validation errors
    """
    serializer = ContactInquirySerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        inquiry = serializer.save()
        
        # Optional: Send confirmation email to user
        try:
            send_mail(
                subject=f'EntreHive: We received your inquiry - {inquiry.subject}',
                message=f"""
Dear {inquiry.name},

Thank you for contacting EntreHive. We have received your inquiry and will get back to you within 24-48 hours.

Inquiry Details:
- Type: {inquiry.get_inquiry_type_display()}
- Subject: {inquiry.subject}
- Reference ID: {inquiry.id}

We appreciate your interest in EntreHive!

Best regards,
The EntreHive Team
support@entrehive.app
                """,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@entrehive.app',
                recipient_list=[inquiry.email],
                fail_silently=True,  # Don't fail if email sending fails
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to send confirmation email: {e}")
        
        return Response(
            {
                'success': True,
                'message': 'Your inquiry has been submitted successfully. We will get back to you soon!',
                'inquiry_id': inquiry.id,
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(
        {
            'success': False,
            'errors': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )

