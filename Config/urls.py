"""
URL configuration for Config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),

    # Public Fact Check APIs
    path('fact_check/', include('fact_check_with_openai.urls')),
    path('image_check/', include('image_fact_check.urls')),

    # Authentication API (Login, User Management, etc.)
    path('auth/', include('auth_app.urls')),

    # Dashboard API (Fact Check History Management)
    path('dashboard/', include('dashboard.urls')),
]
