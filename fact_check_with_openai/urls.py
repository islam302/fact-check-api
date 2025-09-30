from django.urls import path
from .views import FactCheckWithOpenaiView, AnalyticalNewsView

urlpatterns = [
    path("", FactCheckWithOpenaiView.as_view(), name="fact-check"),
    path("analytical_news/", AnalyticalNewsView.as_view(), name="analytical-news"),
]
