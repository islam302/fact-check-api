from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'organization', 
              'role', 'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username field not required since we'll handle email or username
        self.fields[self.username_field].required = False
        # Add email field as an alternative
        self.fields['email'] = serializers.CharField(required=False)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

    def validate(self, attrs):
        # Get username or email from request
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        # Try to find user by username or email
        User = get_user_model()
        user = None

        if email:
            try:
                user = User.objects.get(email=email)
                # Set username for parent validation
                attrs['username'] = user.username
            except User.DoesNotExist:
                pass

        if not user and not username:
            raise serializers.ValidationError('يجب إدخال اسم المستخدم أو البريد الإلكتروني')

        # Call parent validation with username set
        data = super().validate(attrs)
        user = self.user
        data['username'] = user.username
        data['organization'] = getattr(user, 'organization', '')
        data['email'] = getattr(user, 'email', '')
        data['role'] = getattr(user, 'role', '')

        return data

