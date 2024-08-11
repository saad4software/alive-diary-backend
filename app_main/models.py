from django.db import models
from app_account.models import User


class Photo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    datafile = models.ImageField(height_field='height', width_field='width')
    height = models.IntegerField()
    width = models.IntegerField()
    user = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.datafile.name


class Conversation(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name="conversations",  to_field='id', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Message(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    user = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name="messages", to_field='id', on_delete=models.CASCADE)

    text = models.TextField(null=True, blank=True)
    is_user = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class Diary(models.Model):

    statusTypes = (
        ('E', 'Empty'),
        ('B', 'Building'),
        ('R', 'Ready'),
    )

    status = models.CharField(max_length=1, choices=statusTypes, default="E")

    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    user = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE)
    readers = models.ManyToManyField(User, related_name="diaries", blank=True)
    conversations = models.ManyToManyField(Conversation, blank=True)

    path = models.CharField(max_length=255, null=True, blank=True)
    is_built = models.BooleanField(default=False)
    last_built = models.DateTimeField(null=True, blank=True)

    title = models.CharField(max_length=255, null=True, blank=True)
    is_memory = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username

