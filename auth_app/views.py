from rest_framework import generics, viewsets, status
from .models import CustomUser
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from .permissions import IsSuperUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .utils import send_reset_password_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAdminUser
from django.utils.timezone import localtime
from django.db import models, connection
import os
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for complete CRUD operations on all users (both admin and regular users)
    Only accessible by admin users (is_staff=True)

    Endpoints:
    - GET /api/auth/users/ - List all users
    - POST /api/auth/users/ - Create new user
    - GET /api/auth/users/{id}/ - Get specific user
    - PUT /api/auth/users/{id}/ - Update user
    - PATCH /api/auth/users/{id}/ - Partial update user
    - DELETE /api/auth/users/{id}/ - Delete user
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None  # Disable pagination

    def get_queryset(self):
        # Return all users ordered by date joined
        return CustomUser.objects.all().order_by('-date_joined')

    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()

            # Prevent deleting yourself
            if str(user.id) == str(request.user.id):
                return Response(
                    {'error': 'لا يمكنك حذف حسابك الخاص'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            username = user.username
            user_id = str(user.id)

            # Delete related admin log entries manually first to avoid UUID/integer mismatch
            with connection.cursor() as cursor:
                # Delete from django_admin_log where user_id matches (casting both to text for comparison)
                cursor.execute("DELETE FROM django_admin_log WHERE CAST(user_id AS TEXT) = %s", [user_id])

            # Now delete the user (using _raw_delete to bypass Django's collector which causes the error)
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM auth_app_customuser WHERE CAST(id AS TEXT) = %s", [user_id])

            return Response(
                {'message': f'تم حذف المستخدم {username} بنجاح'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AuthenticationView(APIView):
    """
    Unified Authentication View
    Handles both regular login and admin dashboard login
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Login endpoint
        Endpoint: /api/auth/login/
        Accepts: username or email, password
        Optional: is_dashboard=true for dashboard login (requires admin)
        """
        serializer = CustomTokenObtainPairSerializer(data=request.data, context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get user
        username = request.data.get('username')
        email = request.data.get('email')
        is_dashboard = request.data.get('is_dashboard', False)

        user = None
        try:
            if email:
                user = User.objects.get(email=email)
            elif username:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'المستخدم غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if dashboard login
        if is_dashboard:
            if not (user.is_staff or user.is_superuser):
                return Response(
                    {'error': 'يمكن للمسؤولين فقط الوصول إلى لوحة التحكم'},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'تم تسجيل الدخول بنجاح',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'organization': user.organization,
                'role': user.role,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class RegistrationView(APIView):
    """
    Unified Registration View
    Handles both admin and regular user registration
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Registration endpoint
        Endpoint: /api/auth/register/
        Accepts: username, email, password, organization (optional), user_type (admin/user)
        """
        user_type = request.data.get('user_type', 'user')  # Default to 'user'

        if user_type not in ['admin', 'user']:
            return Response(
                {'error': 'نوع المستخدم يجب أن يكون admin أو user'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            # Check if username already exists
            if User.objects.filter(username=request.data.get('username')).exists():
                return Response(
                    {'error': 'اسم المستخدم موجود بالفعل'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if email already exists
            if User.objects.filter(email=request.data.get('email')).exists():
                return Response(
                    {'error': 'البريد الإلكتروني موجود بالفعل'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user based on type
            if user_type == 'admin':
                user = serializer.save(role='admin', is_staff=True)
                message = 'تم تسجيل المسؤول بنجاح'
            else:
                user = serializer.save(role='user', is_staff=False)
                message = 'تم تسجيل المستخدم بنجاح'

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': message,
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'organization': user.organization,
                    'role': user.role,
                    'is_staff': user.is_staff,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """
    Unified Password Reset View
    Handles both password reset request and confirmation
    """
    permission_classes = [AllowAny]

    def post(self, request, uidb64=None, token=None):
        """
        Password Reset endpoint

        For requesting reset:
        Endpoint: POST /api/auth/password-reset/
        Body: {"email": "user@example.com"}

        For confirming reset:
        Endpoint: POST /api/auth/password-reset/{uidb64}/{token}/
        Body: {"password": "new_password"}
        """

        # If no uidb64 and token, this is a password reset request
        if uidb64 is None and token is None:
            email = request.data.get("email")
            if not email:
                return Response(
                    {"error": "يرجى إدخال البريد الإلكتروني"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user = User.objects.get(email=email)
                success = send_reset_password_email(user)
                if success:
                    return Response({
                        "message": "تم إرسال بريد إعادة تعيين كلمة المرور بنجاح."
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"error": "فشل الارسال يرجي التحقق من الايميل"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            except User.DoesNotExist:
                return Response(
                    {"error": "هذا المستخدم غير موجود"},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Otherwise, this is a password reset confirmation
        else:
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response(
                    {"error": "رابط غير صالح"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not default_token_generator.check_token(user, token):
                return Response(
                    {"error": "الرابط غير صالح أو منتهي الصلاحية"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            password = request.data.get("password")
            if not password:
                return Response(
                    {"error": "كلمة المرور مطلوبة"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(password)
            user.save()

            return Response({
                "message": "تم إعادة تعيين كلمة المرور بنجاح"
            }, status=status.HTTP_200_OK)
