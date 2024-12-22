from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', AccountRegisterView.as_view()),
    path('activate/', AccountActivateView.as_view()),

    path('login/', AccountLoginView.as_view()),
    path('refresh/', AccountRefreshTokenView.as_view()),

    path('code/', AccountSendCodeView.as_view()),
    path('forgot/', AccountForgotPasswordView.as_view()),

    path('password/', AccountChangePasswordView.as_view()),
    path('details/', AccountDetailsView.as_view()),
]
