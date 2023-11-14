from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField()

class Friend(models.Model):
    # Define the two users who are friends
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1_friends')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2_friends')
    last_message_date = models.DateTimeField(auto_now_add=True)

class Media(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    reposter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reposter')
    media = models.FileField(upload_to='media/',null=True, blank=True)
    description = models.TextField()
    upload_date = models.DateTimeField()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_media = models.ForeignKey(Media, on_delete=models.CASCADE)
    liked_date = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='comment_media')
    comment = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)

class Shared(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='shared_media')

class ProfileImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.FileField(upload_to='profile_images/', null=True, blank=True, default='https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png')
