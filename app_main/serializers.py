from rest_framework import serializers
from app_main.models import *
import operator
from django.db.models import Q
from functools import reduce
import re


class PhotoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='datafile', read_only=True)

    class Meta:
        model = Photo
        fields = [
            'created',
            'datafile',
            'width',
            'height',
            'name',
            'id'
        ]
        read_only_fields = ['created', 'datafile', 'width', 'height', 'name', 'id']


class ConversationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = [
            'created',
            'active',
            'id'
        ]
        read_only_fields = ['id']


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = [
            'created',
            'active',

            'text',
            'is_user',
            'conversation',
            
            'id'
        ]
        read_only_fields = ['id']



class DiarySerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)


    class Meta:
        model = Diary
        fields = [
            'created',
            'active',
            'first_name',
            'last_name',

            'title',
            'is_memory',

            'status',
            'is_built',
            'last_built',
            
            'id'
        ]
        read_only_fields = ['id', 'is_memory', 'status', 'active', 'is_built']





