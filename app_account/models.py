from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta, datetime
import random


class User(AbstractUser):
    userTypes = (
        ('A', 'Admin'),
        ('C', 'Client'),
    )

    role = models.CharField(max_length=1, choices=userTypes, default="C")

    hobbies = models.CharField(max_length=255, null=True, blank=True)
    job = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    country_code = models.CharField(max_length=10, null=True, blank=True)
    expiration_date = models.DateTimeField(default=datetime.now()+timedelta(days=30))


class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, default=random.randint(111111, 999999))
    email = models.EmailField()
    expiration_date = models.DateTimeField(default=datetime.now()+timedelta(days=1))

    def __str__(self):
        return self.user.username


class Notification(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    seen = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
