from rest_framework import serializers
from app_main.models import *

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
            'id'
        ]
        read_only_fields = [
            'id', 
            'is_memory', 
            'active', 
        ]


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

