import os
from rest_framework.viewsets import ModelViewSet
from common.utils import StandardResultsSetPagination, CustomRenderer, BrowsableAPIRenderer, is_valid_email
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import *
from .filters import *
import rest_framework.filters
from django.conf import settings
from django_filters import rest_framework as filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
import common.msgs as msgs
import operator
from django.db.models import Q
from functools import reduce
from django.core.mail import send_mail
from rest_framework import generics, status
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.core import mail
import time
import threading
import re
import json
import datetime

from django.utils.translation import get_language_from_request
from rest_framework.pagination import PageNumberPagination

# gemini
import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown


class ConversationViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, )
    lookup_field = 'id'
    serializer_class = ConversationSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]
    filter_backends = [filters.DjangoFilterBackend, rest_framework.filters.SearchFilter]
    filterset_class = ConversationDataFilter
    search_fields = ['messages__text']

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by("-created")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response("success")


class MessageViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, )
    lookup_field = 'id'
    serializer_class = MessageSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]
    filter_backends = [filters.DjangoFilterBackend, rest_framework.filters.SearchFilter]
    filterset_class = MessageDataFilter
    search_fields = ['text']

    def get_queryset(self):
        return Message.objects.filter(user=self.request.user).order_by("-created")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response("success")


class DiaryViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, )
    lookup_field = 'id'
    serializer_class = DiarySerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]
    filter_backends = [filters.DjangoFilterBackend, rest_framework.filters.SearchFilter]
    search_fields = ['text']

    def get_queryset(self):
        return Diary.objects.filter(user=self.request.user).order_by("-created")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response("success")




genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}


class DiariesCreateView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


    def init_model(self, conversation, lang):
        model = genai.GenerativeModel(
          model_name="gemini-1.5-flash",
          generation_config=generation_config,
          # safety_settings = Adjust safety settings
          # See https://ai.google.dev/gemini-api/docs/safety-settings
          system_instruction=f"you are a therapist who deeply care about your patient, you want to know how was your patient's day using open short questions and sympathetic simple language, don't use emojis or smilies, you speak in {'English' if lang=='en' else 'Arabic'}",
        )

        messages = conversation.messages.order_by("created")
        lst = list(map(lambda msg: {"role": "user" if msg.is_user else "model", "parts":[msg.text]}, messages))
        self.chat_session = model.start_chat(
            history=lst
        )




    def get(self, request, **kwargs):

        diary = Diary.objects.filter(
                    id=kwargs['id'], 
                    readers__id=request.user.id, 
                    is_memory=False,
                    ).first()

        if not diary: 
            raise APIException("invalid_id")

        conversation_query = Conversation.objects.filter(
            user=request.user, 
            created__date=datetime.date.today(),
        )
        if conversation_query.exists():
            conversation = conversation_query.first()
        else:
            conversation = Conversation(user=request.user)
            conversation.save()


        lang_code = get_language_from_request(request)
        self.init_model(conversation, lang_code)
        hello_msg = "hello again" if conversation_query.exists else "hello" 
        ai_response = self.chat_session.send_message(hello_msg)
        ai_message = Message(
            text=ai_response.text, 
            # text=msg, 
            user=request.user, 
            conversation=conversation,
            is_user=False
        )
        ai_message.save()
        return Response(MessageSerializer(ai_message).data)


    def post(self, request, **kwargs):

        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            raise APIException(serializer.errors)

        message = serializer.save(
            user=request.user,
            is_user=True,
        )
        diary = Diary.objects.filter(
                    id=kwargs['id'], 
                    readers__id=request.user.id, 
                    is_memory=False,
                    ).first()

        if not diary: 
            raise APIException("invalid_id")

        lang_code = get_language_from_request(request)
        self.init_model(message.conversation, lang_code)
        ai_response = self.chat_session.send_message(message.text)
        ai_message = Message(
            text=ai_response.text, 
            # text=msg, 
            user=request.user, 
            conversation=message.conversation,
            is_user=False
        )
        ai_message.save()


        return Response(MessageSerializer(ai_message).data)



class DiariesView(APIView, PageNumberPagination):
    permission_classes = (IsAuthenticated, )
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]
    pagination_class = StandardResultsSetPagination

    page_size = 10


    def get(self, request, **kwargs):
        user = request.user
        diaries = Diary.objects.filter(readers__id=user.id, is_memory=False).order_by('user__first_name')
        page = self.paginate_queryset(diaries, request, view=self)
        return self.get_paginated_response(DiarySerializer(page, many=True).data)


    def post(self, request, **kwargs):

        diary_query = Diary.objects.filter(
            user=request.user,
            is_memory=False,
        )

        if diary_query.exists():
            diary = diary_query.first()
        else:
            diary = Diary(user=request.user)
            diary.save() # to get an id
            diary.readers.add(request.user)
            diary.save()


        return Response(DiarySerializer(diary).data)


    def delete(self, request, **kwargs):
        item = Diary.objects.filter(id=kwargs['id'], user=request.user).first()
        if not item: 
            raise APIException("invalid_id")

        item.delete()

        return Response("success")




class DiariesConversationsView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


    def init_model(self, diary, lang):
        self.model = genai.GenerativeModel(
          model_name="gemini-1.5-flash",
          generation_config=generation_config,

        )

        conversations = diary.conversations.order_by("created")
        self.prompt = [
          f"You are {diary.user.first_name.title()} {diary.user.last_name.title()} diary, you talk like him, use his logic and answer questions as he does, don't use emojis or smilies, you speak in {'English' if lang=='en' else 'Arabic'}",
        ]

        for conv in conversations:
            for msg in conv.messages.order_by("created"):
                segment_1 = "output" if msg.is_user else "input"
                self.prompt += [f"{segment_1}: {msg.text}"]


    def get(self, request, **kwargs):

        item = Diary.objects.filter(id=kwargs['id'], readers__id=request.user.id).first()
        if not item: 
            raise APIException("invalid_id")

        lang_code = get_language_from_request(request)

        self.init_model(item, lang_code)
        self.prompt += ["input: who are you?", "output: "]
        ai_response = self.model.generate_content(self.prompt)
        conversation = Conversation(user=request.user)
        conversation.save()

        ai_message = Message(
            text=ai_response.text, 
            user=request.user, 
            conversation=conversation,
            is_user=False
        )
        ai_message.save()

        return Response(MessageSerializer(ai_message).data)



    def post(self, request, **kwargs):

        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            raise APIException(serializer.errors)

        item = Diary.objects.filter(id=kwargs['id'], readers__id=request.user.id).first()
        if not item: 
            raise APIException("invalid_id")

        self.init_model(item)
        message = serializer.save(
            user=request.user,
            is_user=True,
        )
        self.prompt += [f"input: {message.text}", "output: "]
        ai_response = self.model.generate_content(self.prompt)
        ai_message = Message(
            text=ai_response.text, 
            user=request.user, 
            conversation=message.conversation,
            is_user=False
        )
        ai_message.save()

        return Response(MessageSerializer(ai_message).data)


    def delete(self, request, **kwargs):
        item = Diary.objects.filter(id=kwargs['id'], user=request.user).first()

        if not item: 
            raise APIException("invalid_id")

        item.delete()
        return Response("success")

class DiariesShareView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


    def get(self, request, **kwargs):
        user = request.user
        email = request.GET.get('email')
        email_user = User.objects.filter(username=email).first()
        if not email_user:
            raise APIException("invalid_email")
        diary = Diary.objects.filter(id=kwargs['id'], user=request.user).first()
        if not diary:
            raise APIException("invalid_id")

        if email_user not in diary.readers.all(): diary.readers.add(email_user)
        diary.save()

        return Response("success")





class MemoriesView(APIView, PageNumberPagination):
    permission_classes = (IsAuthenticated, )
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]
    pagination_class = StandardResultsSetPagination

    page_size = 10

    def get(self, request, **kwargs):
        user = request.user
        diaries = Diary.objects.filter(readers__id=user.id, is_memory=True).order_by('-created')
        page = self.paginate_queryset(diaries, request, view=self)
        return self.get_paginated_response(DiarySerializer(page, many=True).data)


    def post(self, request, **kwargs):

        serializer = DiarySerializer(data=request.data)
        if not serializer.is_valid():
            raise APIException(serializer.errors)


        diary = Diary(user=request.user, is_memory=True, title=serializer.validated_data.get("title"))
        diary.save()

        diary.readers.add(request.user)
        diary.save()


        return Response(DiarySerializer(diary).data)


    def delete(self, request, **kwargs):
        item = Diary.objects.filter(id=kwargs['id'], user=request.user).first()

        if not item: 
            raise APIException("invalid_id")

        item.delete()

        return Response("success")


class MemoriesConversationsView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


    def init_model(self, diary):
        self.model = genai.GenerativeModel(
          model_name="gemini-1.5-flash",
          generation_config=generation_config,

        )

        conversations = diary.conversations.order_by("created")

        self.prompt = [
          f"You are a memory, be as clear as possible, use short clear description from the third person point of view, don't use emojis or smilies",
        ]

        for conv in conversations:
            for msg in conv.messages.order_by("created"):
                segment_1 = "output" if msg.is_user else "input"
                self.prompt += [f"{segment_1}: {msg.text}"]




    def get(self, request, **kwargs):

        item = Diary.objects.filter(id=kwargs['id'], readers__id=request.user.id, is_memory=True).first()
        if not item: 
            raise APIException("invalid_id")


        self.init_model(item)
        self.prompt += ["input: describe the memory for me", "output: "]
        ai_response = self.model.generate_content(self.prompt)
        conversation = Conversation(user=request.user)
        conversation.save()

        ai_message = Message(
            text=ai_response.text, 
            user=request.user, 
            conversation=conversation,
            is_user=False
        )
        ai_message.save()

        return Response(MessageSerializer(ai_message).data)



    def post(self, request, **kwargs):

        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            raise APIException(serializer.errors)

        item = Diary.objects.filter(id=kwargs['id'], readers__id=request.user.id).first()
        if not item: 
            raise APIException("invalid_id")

        self.init_model(item)
        message = serializer.save(
            user=request.user,
            is_user=True,
        )
        self.prompt += [f"input: {message.text}", "output: "]
        ai_response = self.model.generate_content(self.prompt)
        ai_message = Message(
            text=ai_response.text, 
            user=request.user, 
            conversation=message.conversation,
            is_user=False
        )
        ai_message.save()

        return Response(MessageSerializer(ai_message).data)


    def delete(self, request, **kwargs):
        item = Diary.objects.filter(id=kwargs['id'], user=request.user, is_memory=True).first()

        if not item: 
            raise APIException("invalid_id")

        item.delete()
        return Response("success")


class MemoryCreateView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


    def init_model(self, conversation, lang):
        model = genai.GenerativeModel(
          model_name="gemini-1.5-flash",
          generation_config=generation_config,
          # safety_settings = Adjust safety settings
          # See https://ai.google.dev/gemini-api/docs/safety-settings
          system_instruction=f"you are trying to capture the moment, get as much details as you can about the date, time, place, weather, what they can see, hear, taste, and feel. use one question at the time, use 'you' pronoun, don't use emojis or smilies, you speak in {'English' if lang=='en' else 'Arabic'}",
        )

        messages = conversation.messages.order_by("created")
        
        lst = list(map(lambda msg: {"role": "user" if msg.is_user else "model", "parts":[msg.text]}, messages))

        self.chat_session = model.start_chat(
            history=lst
        )




    def get(self, request, **kwargs):

        diary = Diary.objects.filter(
            id=kwargs['id'], 
            readers__id=request.user.id, 
            is_memory=True,
            ).first()

        if not diary: 
            raise APIException("invalid_id")


        conversation = Conversation(user=request.user)
        conversation.save()
        diary.conversations.add(conversation)
        diary.save()

        lang_code = get_language_from_request(request)
        self.init_model(conversation, lang_code)
        ai_response = self.chat_session.send_message("hi")
        ai_message = Message(
            text=ai_response.text, 
            # text=msg, 
            user=request.user, 
            conversation=conversation,
            is_user=False
        )
        ai_message.save()

        return Response(MessageSerializer(ai_message).data)


    def post(self, request, **kwargs):

        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            raise APIException(serializer.errors)

        message = serializer.save(
            user=request.user,
            is_user=True,
        )

        lang_code = get_language_from_request(request)
        self.init_model(message.conversation, lang_code)
        ai_response = self.chat_session.send_message(message.text)
        ai_message = Message(
            text=ai_response.text, 
            # text=msg, 
            user=request.user, 
            conversation=message.conversation,
            is_user=False
        )
        ai_message.save()

        return Response(MessageSerializer(ai_message).data)


