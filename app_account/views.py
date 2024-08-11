from rest_framework.exceptions import APIException
from rest_framework import generics, status
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from common.utils import CustomRenderer
from . import msgs
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect


class AccountLoginView(TokenViewBase):
    serializer_class = LoginSerializer
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


class AccountRefreshTokenView(TokenViewBase):
    serializer_class = RefreshTokenSerializer
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


class AccountRegisterView(generics.CreateAPIView):
    permission_classes = ()

    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]

    def perform_create(self, serializer):
        serializer.save()


class AccountActivateView(APIView):
    permission_classes = ()
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]

    def get(self, request):
        user_id = request.GET.get("user") if "user" in request.GET else "0"
        code = request.GET.get("code") if "code" in request.GET else ""
        verification_query = VerificationCode.objects.filter(user__id=user_id, code=code).first()
        if not verification_query:
            raise APIException("not_found")

        verification_query.delete()
        return redirect('https://campaigny.net/account/login')


    def post(self, request, *args, **kwargs):
        success = ActivateSerializer(data=request.data, context=request).is_valid()
        if success:
            return Response(msgs.success)
        else:
            raise APIException(msgs.invalid_credentials)


class AccountForgotPasswordView(APIView):
    permission_classes = ()
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response(msgs.success)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountSendCodeView(APIView):
    permission_classes = ()
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]

    def post(self, request, *args, **kwargs):
        serializer = SendCodeSerializer(data=request.data)

        if serializer.is_valid():
            return Response(msgs.success)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountDetailsView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]

    def get(self, request):
        serializer = UpdateSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = UpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountPasswordView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context=request)
        if serializer.is_valid():
            serializer.change_password(serializer.data)
            return Response(msgs.success)

        raise APIException(msgs.invalid_credentials)

