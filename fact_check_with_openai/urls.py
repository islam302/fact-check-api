from django.urls import path
from .views import FactCheckWithOpenaiView

urlpatterns = [
    path("", FactCheckWithOpenaiView.as_view(), name="fact-check"),
]
