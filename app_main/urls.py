from django.urls import path, include
from .views import *

diaries_list = DiaryViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

diaries_details = DiaryViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


memories_list = MemoriesViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

memories_details = MemoriesViewSet.as_view({
    'delete': 'destroy'
})

urlpatterns = [
    path('diaries/', diaries_list),
    path('diaries/<int:id>/', diaries_details),
    path('conversation/', ConversationsView.as_view()),
    path('diaries/conversation/', DiaryConversationsView.as_view()),

    path('memories/', memories_list),
    path('memories/<int:id>/', memories_details),
    path('memories/<int:id>/create/', MemoryCreateView.as_view()),
    path('memories/<int:id>/talk/', MemoryConversationsView.as_view()),

]
