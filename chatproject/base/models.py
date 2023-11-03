from django.db import models

# Create your models here.
class ChatModel(models.Model):
    sender = models.CharField(max_length=100)
    message = models.CharField(max_length=500)
    