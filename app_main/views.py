from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from common.utils import CustomRenderer, StandardResultsSetPagination
import rest_framework.filters
from django_filters import rest_framework as filters
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
import datetime
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from .gemini_script import create_diary_session, talk_to_diary, create_memory_session, talk_to_memory


class DiaryViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, )
    lookup_field = 'id'
    serializer_class = DiarySerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]
    filter_backends = [filters.DjangoFilterBackend, rest_framework.filters.SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        return Diary.objects.filter(user=self.request.user).order_by("-created")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response("success")


class ConversationsView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]

    def get_conversation(self):
        diary = Diary.objects.filter(
                    user=self.request.user,
                    is_memory=False,
                ).first()

        if not diary: 
            diary = Diary(
                user=self.request.user, 
                is_memory=False,
                title="My diary",
            )
            diary.save()

            print("created a new diary")
            print(f"new diary id is {diary.id}")


        conversation = Conversation.objects.filter(
            diary=diary,
            created__date=datetime.date.today(),
        ).first()

        if not conversation:
            conversation = Conversation(
                diary=diary,
            )
            conversation.save()

        return conversation

    def get(self, request, **kwargs):

        conversation = self.get_conversation()

        messages = conversation.messages.order_by("created")
        history = list(map(lambda msg: {"role": "user" if msg.is_user else "model", "parts":[msg.text]}, messages))
        chat_session = create_diary_session(history)

        ai_response = chat_session.send_message("hello")

        ai_message = Message(
            text=ai_response.text, 
            conversation=conversation,
            is_user=False
        )
        ai_message.save()

        return Response(MessageSerializer(ai_message).data)


    @swagger_auto_schema(request_body=MessageSerializer)
    def post(self, request, **kwargs):

        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            raise APIException(serializer.errors)

        conversation = self.get_conversation()

        message = serializer.save(
            conversation=conversation,
            is_user=True,
        ) # save users message

        # ai_response = "hello world again" # get ai response
        messages = conversation.messages.order_by("created")
        history = list(map(lambda msg: {"role": "user" if msg.is_user else "model", "parts":[msg.text]}, messages))
        chat_session = create_diary_session(history)

        ai_response = chat_session.send_message(message.text)

        ai_message = Message(
            text=ai_response.text, 
            conversation=conversation,
            is_user=False
        ) # save ai response message
        ai_message.save()

        return Response(MessageSerializer(ai_message).data)


class DiaryConversationsView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


    def get_diary(self):
        diary = Diary.objects.filter(
                    user=self.request.user,
                    is_memory=False,
                ).first()

        if not diary: 
            diary = Diary(
                user=self.request.user, 
                is_memory=False,
                title="My diary",
            )
            diary.save()

        return diary

    def get(self, request, **kwargs):

        diary = self.get_diary()
        conversations = diary.conversations.order_by("-created")

        prompt = [
          f"You are {diary.user.first_name.title()} {diary.user.last_name.title()} diary, you talk like him, use his logic and answer questions as he does, don't use emojis or smilies",
        ]

        for conv in conversations:
            print(conv)
            for msg in conv.messages.order_by("created"):
                print(msg.text)
                segment_1 = "output" if msg.is_user else "input"
                prompt += [f"{segment_1}: {msg.text}"]

        prompt += ["input: who are you", "output: "]

        print(prompt)

        ai_response = talk_to_diary(prompt)

        # conversation = Conversation(diary=diary)
        # conversation.save()

        ai_message = Message(
            text=ai_response, 
            conversation=conversations.last(),
            is_user=False
        )
        # ai_message.save()

        return Response(MessageSerializer(ai_message).data)


    @swagger_auto_schema(request_body=MessageSerializer)
    def post(self, request, **kwargs):

        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            raise APIException(serializer.errors)


        diary = self.get_diary()
        conversations = diary.conversations.order_by("-created")

        prompt = [
          f"You are {diary.user.first_name.title()} {diary.user.last_name.title()} diary, you talk like him, use his logic and answer questions as he does, don't use emojis or smilies",
        ]

        for conv in conversations:
            print(conv)
            for msg in conv.messages.order_by("created"):
                print(msg.text)
                segment_1 = "output" if msg.is_user else "input"
                prompt += [f"{segment_1}: {msg.text}"]

        prompt += [f"input: {serializer.validated_data.get('text')}", "output: "]

        print(prompt)

        ai_response = talk_to_diary(prompt)

        # conversation = Conversation(diary=diary)
        # conversation.save()

        ai_message = Message(
            text=ai_response, 
            conversation=conversations.last(),
            is_user=False
        )
        # ai_message.save()

        return Response(MessageSerializer(ai_message).data)


class MemoriesViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, )
    lookup_field = 'id'
    serializer_class = DiarySerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]
    filter_backends = [filters.DjangoFilterBackend, rest_framework.filters.SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        return Diary.objects.filter(
            user=self.request.user, 
            is_memory=True,
        ).order_by("-created")

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user, 
            is_memory=True,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response("success")


class MemoryCreateView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


    def get_conversation(self, memory_id):
        memory = Diary.objects.filter(
                    id=memory_id,
                    user=self.request.user,
                    is_memory=True,
                ).first()

        if not memory: 
            raise APIException("invalid_id")


        conversation = Conversation.objects.filter(
            diary=memory,
        ).first()

        if not conversation:
            conversation = Conversation(
                diary=memory,
            )
            conversation.save()

        return conversation


    def get(self, request, **kwargs):

        conversation = self.get_conversation(kwargs['id'])

        messages = conversation.messages.order_by("created")
        history = list(map(lambda msg: {
            "role": "user" if msg.is_user else "model", 
            "parts":[msg.text]}, messages))

        chat_session = create_memory_session(history)

        ai_response = chat_session.send_message("hi")

        ai_message = Message(
            text=ai_response.text, 
            conversation=conversation,
            is_user=False
        )
        ai_message.save()

        return Response(MessageSerializer(ai_message).data)


    @swagger_auto_schema(request_body=MessageSerializer)
    def post(self, request, **kwargs):

        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            raise APIException(serializer.errors)

        conversation = self.get_conversation(kwargs['id'])

        message = serializer.save(
            conversation=conversation,
            is_user=True,
        ) # save users message

        # ai_response = "hello world again" # get ai response
        messages = conversation.messages.order_by("created")
        history = list(map(lambda msg: {
            "role": "user" if msg.is_user else "model", 
            "parts":[msg.text]}, messages))

        chat_session = create_memory_session(history)

        ai_response = chat_session.send_message(message.text)

        ai_message = Message(
            text=ai_response.text, 
            conversation=conversation,
            is_user=False
        ) # save ai response message
        ai_message.save()

        return Response(MessageSerializer(ai_message).data)


class MemoryConversationsView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = [CustomRenderer, BrowsableAPIRenderer]


    def get(self, request, **kwargs):

        memory = Diary.objects.filter(
            id=kwargs['id'], 
            is_memory=True,
        ).first()

        conversations = memory.conversations.order_by("-created")

        prompt = [
            "You are a memory, be as clear as possible, use short clear description from the third person point of view, don't use emojis"
        ]

        for conv in conversations:
            for msg in conv.messages.order_by("created"):
                segment_1 = "output" if msg.is_user else "input"
                prompt += [f"{segment_1}: {msg.text}"]

        prompt += ["input: describe the memory for me", "output: "]

        ai_response = talk_to_diary(prompt)

        # conversation = Conversation(diary=diary)
        # conversation.save()

        ai_message = Message(
            text=ai_response, 
            conversation=conversations.last(),
            is_user=False
        )
        # ai_message.save()

        return Response(MessageSerializer(ai_message).data)


    @swagger_auto_schema(request_body=MessageSerializer)
    def post(self, request, **kwargs):

        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            raise APIException(serializer.errors)


        memory = Diary.objects.filter(
            id=kwargs['id'], 
            is_memory=True,
        ).first()

        conversations = memory.conversations.order_by("-created")

        prompt = [
            "You are a memory, be as clear as possible, use short clear description from the third person point of view, don't use emojis"
        ]

        for conv in conversations:
            for msg in conv.messages.order_by("created"):
                segment_1 = "output" if msg.is_user else "input"
                prompt += [f"{segment_1}: {msg.text}"]

        prompt += [f"input: {serializer.validated_data.get('text')}", "output: "]

        print(prompt)

        ai_response = talk_to_diary(prompt)

        # conversation = Conversation(diary=diary)
        # conversation.save()

        ai_message = Message(
            text=ai_response, 
            conversation=conversations.last(),
            is_user=False
        )
        # ai_message.save()

        return Response(MessageSerializer(ai_message).data)



