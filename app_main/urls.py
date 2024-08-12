from django.urls import path, include
from .views import *


conversations_list = ConversationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

conversations_details = ConversationViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


messages_list = MessageViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

messages_details = MessageViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


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



urlpatterns = [
    path('account/', include('app_account.urls')),

    path('conversations/', conversations_list),
    path('conversations/<int:id>/', conversations_details),

    path('messages/', messages_list),
    path('messages/<int:id>/', messages_details),

    path('diaries/', diaries_list),
    path('diaries/<int:id>/', diaries_details),

    # path('conversations/start/', ConversationView.as_view()),

    path('diaries/list/', DiariesView.as_view()),
    path('diaries/list/<int:id>/', DiariesView.as_view()),
    path('diaries/list/<int:id>/start/', DiariesConversationsView.as_view()),
    path('diaries/list/<int:id>/create/', DiariesCreateView.as_view()),
    path('diaries/list/<int:id>/share/', DiariesShareView.as_view()),


    path('memories/list/', MemoriesView.as_view()),
    path('memories/list/<int:id>/', MemoriesView.as_view()),
    path('memories/list/<int:id>/create/', MemoryCreateView.as_view()),
    path('memories/list/<int:id>/start/', MemoriesConversationsView.as_view()),
    path('memories/list/<int:id>/share/', DiariesShareView.as_view()),


]

