from django.apps import AppConfig

class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'  # Changed from 'user' to 'auth_app' to avoid conflict with django.contrib.auth

    def ready(self):
        import auth_app.signals
