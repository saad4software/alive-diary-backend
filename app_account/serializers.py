from rest_framework import serializers
from app_account.models import *
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from . import msgs
from django.core.mail import send_mail
from django.conf import settings
import time

class UpdateSerializer(serializers.ModelSerializer):

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
        read_only_fields = ('username', 'role' )


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        username = attrs['username']
        user = get_user_model().objects.filter(username=username).first()

        if not user or not user.check_password(attrs['password']):
            raise serializers.ValidationError(msgs.invalid_credentials)

        active = not VerificationCode.objects.filter(user__id=user.id, email=user.username).exists()
        if not active:
            raise serializers.ValidationError(msgs.not_active)

        if user.expiration_date and user.role == "C" and user.expiration_date < timezone.now():
            raise serializers.ValidationError(msgs.expired_account)

        refresh = self.get_token(user)
        notifications_count = Notification.objects.filter(user=user, seen=False).count()

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UpdateSerializer(user).data,
            'role': user.role,
            'notifications': notifications_count,
        }

        # time.sleep(5)

        return data


class RefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        decoded_payload = token_backend.decode(data['access'], verify=True)
        user_id = decoded_payload['user_id']
        user = User.objects.get(id=user_id)

        if user.expiration_date and user.role == "C" and user.expiration_date < timezone.now():
            raise serializers.ValidationError(msgs.expired_account)

        notifications_count = Notification.objects.filter(user=user, seen=False).count()
        data['role'] = user.role
        data['notifications'] = notifications_count
        data['user'] = UpdateSerializer(user).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        user = self.context.user
        if not user.check_password(data.get('password')):
            raise serializers.ValidationError(msgs.wrong_password)
        return data

    def change_password(self, validate_data):
        user = self.context.user
        user.set_password(validate_data.get('new_password'))
        user.save()


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(msgs.no_match)
        return data

    def create(self, validated_data):
        data = {
            key: value for key, value in validated_data.items()
            if key not in ('password1', 'password2')
        }
        data['password'] = validated_data['password1']

        user = self.Meta.model.objects.create_user(**data)

        # email verification code, assumed username is email!
        code = VerificationCode(user=user, email=user.username)
        code.save()

        # the context is the request
        base_url = self.context['request'].build_absolute_uri('/')

        send_mail(
            'Welcome to Alive Diary! 🚀',

f"""
Dear {user.first_name} {user.last_name},

Welcome aboard! 🎉                                                                                                                                 

Your activation code is {code.code}
You can also follow this link {base_url}api/account/activate/?code={code.code}&user={user.id}

Best regards,
Alive Diary team with ❤️

"""
            ,
            f'AliveDiary<{settings.EMAIL_SENDER}>',
            [data['username']],
            fail_silently=False,
            )


        return data

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'email',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'country_code',
            'username',
        )
        read_only_fields = ('id',)


class SendCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

    def validate(self, data):
        verification_query = get_user_model().objects.filter(username=data['username']).exists()

        if verification_query:
            self.create(data)
            return data
        raise serializers.ValidationError(msgs.invalid_user)

    def create(self, validated_data):
        user = get_user_model().objects.filter(username=validated_data.get("username")).first()

        # email verification code, assumed username is email!
        code = VerificationCode(user=user, email=user.username)
        code.save()

        send_mail(
            'Password Reset Code',
            'Your password reset code is ' + str(code.code),
            f'Campaigny<{settings.EMAIL_SENDER}>',
            [validated_data.get('username')],
            fail_silently=False,
            )


class ActivateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    def validate(self, data):
        verification_query = VerificationCode.objects.filter(user__username=data['username'], email=data['username']).order_by('-id')
        if verification_query.exists():
            code = verification_query[0]
            success = str(code.code) == str(data['code'])
            if success:
                verification_query.delete()
                return data
            else:
                raise serializers.ValidationError(msgs.invalid_code)

        raise serializers.ValidationError(msgs.already_activated)


class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        verification_query = VerificationCode.objects.filter(user__username=data['username']).order_by('-id')
        if verification_query.exists():
            code = verification_query[0]
            success = str(code.code) == str(data['code'])
            if success:
                verification_query.delete()
                self.reset_password(data)
                return data
            else:
                raise serializers.ValidationError(msgs.invalid_code)

        raise serializers.ValidationError(msgs.no_code)

    def reset_password(self, validated_data):
        # verification_query = VerificationCode.objects.filter(user__username=validated_data['username'])
        # verification_query.delete()

        user = get_user_model().objects.filter(username=validated_data.get('username')).first()
        user.set_password(validated_data.get('new_password'))
        user.save()
