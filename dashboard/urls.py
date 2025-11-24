from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FactCheckHistoryViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r'fact-checks', FactCheckHistoryViewSet, basename='factcheck')

urlpatterns = [
    path('', include(router.urls)),
]
