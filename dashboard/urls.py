from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import FactCheckHistoryViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r'fact-checks', FactCheckHistoryViewSet, basename='factcheck')

urlpatterns = [
    # Token refresh (login is in auth_app)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Include router URLs
    path('', include(router.urls)),
]
