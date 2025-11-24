from auth_app.views import (
    UserViewSet,
    AuthenticationView,
    RegistrationView,
    PasswordResetView,
)
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')


urlpatterns = [

    # Authentication endpoints
    path('login/', AuthenticationView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Registration endpoint
    path('register/', RegistrationView.as_view(), name='register'),

    # Password reset endpoints
    path('password-reset/', PasswordResetView.as_view(), name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', PasswordResetView.as_view(), name='password_reset_confirm'),

    # User CRUD (all routes from UserViewSet)
    path('', include(router.urls)),

]
