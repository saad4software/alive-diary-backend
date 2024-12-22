from rest_framework import serializers
from app_account.models import *
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.state import token_backend
from common.utils import is_valid_email

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            'first_name', 
            'last_name', 
            'username', 
            'country_code', 
            'expiration_date',
            'hobbies',
            'job',
            'bio',
            'role',
        )
        read_only_fields = ['username', 'role',  'expiration_date']


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        username = attrs['username']
        user = get_user_model().objects.filter(username=username).first()

        if not user or not user.check_password(attrs['password']):
            raise serializers.ValidationError("invalid_credentials")

        if not user.is_active:
            raise serializers.ValidationError("not_active")

        refresh = self.get_token(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
            'role': user.role,
        }

        return data


class RefreshTokenSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        decoded_payload = token_backend.decode(data['access'], verify=True)
        user_id = decoded_payload['user_id']
        user = User.objects.get(id=user_id)
        data['role'] = user.role
        data['user'] = UserSerializer(user).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("invalid_email")

        return value


    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("password_dont_match")

        data['password'] = data['password1']

        data.pop('password1', None)
        data.pop('password2', None)

        return data

    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'email',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'country_code',
            'username',
        ]
        read_only_fields = ['id',]


class ActivateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    code = serializers.CharField(required=True)


class SendCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

    def validate_username(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("invalid_email")

        verification_query = get_user_model().objects.filter(username=value).exists()
        if not verification_query:
            raise serializers.ValidationError("invalid_username")

        return value


class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        verification_query = VerificationCode.objects.filter(
            user__username=data['username'],
        ).order_by('-id')

        if not verification_query.exists():
            raise serializers.ValidationError("no_code")

        code = verification_query[0]
        if str(code.code) != str(data['code']):
            raise serializers.ValidationError("invalid_code")

        return data




