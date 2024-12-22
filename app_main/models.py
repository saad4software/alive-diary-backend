from django.db import models
from app_account.models import User


class Diary(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    user = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE)
    readers = models.ManyToManyField(User, related_name="diaries", blank=True)

    title = models.CharField(max_length=255, null=True, blank=True)
    is_memory = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Conversation(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    diary = models.ForeignKey(Diary, related_name="conversations",  to_field='id', on_delete=models.CASCADE)

    def __str__(self):
        return self.diary.title


class Message(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    conversation = models.ForeignKey(Conversation, related_name="messages", to_field='id', on_delete=models.CASCADE)

    text = models.TextField(null=True, blank=True)
    is_user = models.BooleanField(default=True)

    def __str__(self):
        return self.text




