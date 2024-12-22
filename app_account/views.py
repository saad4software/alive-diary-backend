from django.shortcuts import render
from rest_framework import generics, status
from .serializers import *
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from common.utils import CustomRenderer
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema


class AccountDetailsView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data)

        if not serializer.is_valid():
            raise APIException(serializer.errors)

        serializer.save()
        return Response(serializer.data)


class AccountForgotPasswordView(APIView):
    permission_classes = ()
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]

    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # if not serializer.is_valid():
        #     raise APIException(serializer.errors)

        verification_query = VerificationCode.objects.filter(
            user__username=serializer.validated_data.get('username'),
            code=serializer.validated_data.get('code')
        ).order_by('-id')

        verification_query.delete()

        user = get_user_model().objects.filter(
            username=serializer.validated_data.get('username'),
        ).first()
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response("success")


class AccountSendCodeView(APIView):
    permission_classes = ()
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


    @swagger_auto_schema(request_body=SendCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = SendCodeSerializer(data=request.data)

        if not serializer.is_valid():
            raise APIException(serializer.errors)

        user = get_user_model().objects.filter(username=serializer.validated_data.get("username")).first()
        code = VerificationCode(user=user, email=user.username)
        code.save()

        # send_mail(
        #     'Password Reset Code',
        #     'Your password reset code is ' + str(code.code),
        #     f'AliveDiary<{settings.EMAIL_SENDER}>',
        #     [user.username],
        #     fail_silently=False,
        # )

        return Response("success")


class AccountChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            raise APIException(serializer.errors)

        user = request.user
        password = serializer.validated_data.get("password")
        new_password = serializer.validated_data.get("new_password")

        if not user.check_password(password):
            raise APIException("invalid_password")

        user.set_password(new_password)
        user.save()

        return Response("success")

        


class AccountRefreshTokenView(TokenViewBase):
    serializer_class = RefreshTokenSerializer
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


class AccountLoginView(TokenViewBase):
    serializer_class = LoginSerializer
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


class AccountRegisterView(generics.CreateAPIView):
    permission_classes = ()

    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
    renderer_classes = [BrowsableAPIRenderer, CustomRenderer]

    def perform_create(self, serializer):
        user = get_user_model().objects.create_user(**serializer.validated_data, is_active=False)

        # email verification code, assumed username is email!
        code = VerificationCode(user=user, email=user.username)
        code.save()

        # send_mail(
        #     'Welcome to Alive Diary! 🚀',

        #     f"""
        #     Dear {user.first_name} {user.last_name},

        #     Welcome aboard! 🎉                                                                                                                                 

        #     Your activation code is {code.code}

        #     Best regards,
        #     Alive Diary team with ❤️

        #     """
        #     ,
        #     f'AliveDiary<{settings.EMAIL_SENDER}>',
        #     [user.username],
        #     fail_silently=False,
        # )



class AccountActivateView(APIView):
    permission_classes = ()
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]

    @swagger_auto_schema(request_body=ActivateSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ActivateSerializer(data=request.data)

        if not serializer.is_valid():
            raise APIException(serializer.errors)

        verification_query = VerificationCode.objects.filter(
            user__username=serializer.validated_data.get("username"), 
            email=serializer.validated_data.get("username"),
            code=serializer.validated_data.get("code"),
        ).order_by('-id')

        if not verification_query.exists():
            raise APIException("invalid_code")
    
        user = get_user_model().objects.filter(
            username=serializer.validated_data.get("username"),
        ).first()
        user.is_active=True
        user.save()

        verification_query.delete()

        return Response("success")
        






