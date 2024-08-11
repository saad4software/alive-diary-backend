from django.urls import path, include
from .views import *

urlpatterns = [

    path('register/', AccountRegisterView.as_view()),
    path('activate/', AccountActivateView.as_view()),

    path('login/', AccountLoginView.as_view()),
    path('refresh/', AccountRefreshTokenView.as_view()),

    path('forgot/', AccountForgotPasswordView.as_view()),
    path('code/', AccountSendCodeView.as_view()),

    path('password/', AccountPasswordView.as_view()),
    path('details/', AccountDetailsView.as_view()),

]
