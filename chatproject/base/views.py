import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Friend, Message, Media, Shared, Like, Comment
from django.db.models import Q

# TODO: make all only authenticated user usable only

def logout(request):
    auth.logout(request)
    return redirect('/')

def index(request):
    if request.user.is_authenticated:
        current_user = request.user
        medias = None
        if (Media.objects.exists()):
            medias = Media.objects.all().order_by("upload_date")[:20]
        if request.method == 'POST' and request.POST['address'] != '':
            props = request.POST['address'].split('*')
            print('props', props)
            media_owner = User.objects.get(username=props[0])
            media_reposter = User.objects.get(username=props[1])

            date_object = datetime.datetime.strptime(props[2], "%Y-%m-%d %H:%M:%S%z")
            media = Media.objects.get(owner=media_owner, reposter=media_reposter, upload_date=date_object)
            if request.POST['command'] == 'share' and media_owner != current_user:
                print('share')
                shareds = Shared.objects.filter(user=current_user, media=media)
                if (shareds.exists()) or current_user == media_reposter:
                    return redirect('/')
                Media.objects.create(owner=media_owner, reposter=current_user, media=media.media, description=media.description, upload_date=datetime.datetime.now().replace(microsecond=0))
                Shared.objects.create(user=current_user, media=media)
                return render(request, 'index.html', 
                    {'user': current_user, 
                    'medias': collector(request, medias)})
            elif request.POST['command'] == 'like':
                print('like')
                if Like.objects.filter(user=current_user, liked_media=media).exists():
                    return redirect('/')
                Like.objects.create(user=current_user, liked_media=media)
                return redirect('/')
            elif request.POST['command'] == 'dislike':
                print('dislike')
                media_to_delete = Like.objects.filter(user=current_user, liked_media=media)
                if media_to_delete.exists():
                    media_to_delete.first().delete()
                return redirect('/')
            elif request.POST['command'] == 'comment':
                print('comment')
                Comment.objects.create(user=current_user, media=media, comment=request.POST['comment'])
                return redirect('/')
            else:
                print('error')
        return render(request, 'index.html', 
            {'user': current_user, 
            'medias': collector(request, medias)})
    else:
        return redirect('login')

# TODO: 1) validations to be added! 2) and not logged in only requirement
def login(request):
    if request.user.is_authenticated and request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'login.html', {})

# TODO: validations to be added! 2) and not logged in only requirement
def register(request):
    if request.user.is_authenticated is False and request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password != password2:
            messages.info(request, 'Passwords did not match')
            return redirect('register')
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email already registered')
            return redirect('register')
        elif User.objects.filter(username=username).exists():
            messages.info(request, 'username already exists')
            return redirect('register')
        else:
            user = User.objects.create_user(username=username, email=email,password=password)
            user.save()
            return redirect('/')
    else:
        return render(request, 'register.html', {})


def chat(request, room):
    if request.user.is_authenticated:
        user_names = room.split('-')
        current_username = request.user.username
        current_user = request.user
        if len(user_names) != 2 or user_names[0] > user_names[1] or user_names[0] == user_names[1] or (current_username != user_names[0] and current_username != user_names[1]):
            return redirect('/')
        
        recipient = user_names[1]
        if current_username == user_names[1]:
            recipient = user_names[0]
        
        current_recipient = ''
        if User.objects.filter(username=recipient).exists():
            current_recipient = User.objects.get(username=recipient)
        else:
            return redirect('/')
        if  Friend.objects.filter(Q(user1=current_user, user2=current_recipient) | Q(user1=current_recipient,user2=current_user)).exists() is False:
            return redirect('/')
        messages = Message.objects.filter(Q(sender=current_user, recipient=current_recipient) | Q(sender=current_recipient,recipient=current_user)).order_by('timestamp')
        friendship = Friend.objects.filter(Q(user1=current_user, user2=current_recipient) | Q(user1=current_recipient,user2=current_user)).last()
        print("friendship", Friend.objects.filter(Q(user1=current_user, user2=current_recipient) | Q(user1=current_recipient,user2=current_user)).exists())
        friendship.last_message_date = datetime.datetime.now()
        friendship.save()
        return render(request, 'chat.html', {'room': room, 
            'user': current_username, 'recipient': recipient, 'messages':messages})
    else:
        return redirect('/')

def friends_message_view(request):
    current_user = request.user
    friends = Friend.objects.filter(Q(user1=current_user) | Q(user2=current_user)).order_by('last_message_date')
    messages = []
    for friend in friends:
        user1 = friend.user1
        if user1 == current_user:
            user1 = friend.user2
        sender_query = Message.objects.filter(sender=user1, recipient=current_user).order_by('timestamp')
        receiver_query = Message.objects.filter(sender=current_user, recipient=user1).order_by('timestamp')
        sent_message = ''
        received_message = ''
        if len(sender_query) > 0:
            sent_message = sender_query.last()
        if len(receiver_query) > 0:
            received_message = receiver_query.last()

        if (sent_message == '' and received_message == ''):
            messages.append('')
        elif (sent_message == '' and received_message != ''):
            messages.append(received_message)
        elif (sent_message != '' and received_message == ''):
            messages.append(sent_message)
        else:
            if sent_message.timestamp > received_message.timestamp:
                messages.append(sent_message)
            else:
                messages.append(received_message)


    if request.user.is_authenticated:
        zipped = zip(friends, messages)
        return render(request, 'chat_view.html', {'user': current_user,'friends_messages': zipped})
    else:
        return redirect('/')
    
def upload(request):
    if request.method == 'POST':
        user = request.user
        description = request.POST['description_text']
        if len(request.FILES) == 1:
            file = request.FILES['inputFile']
            if file.size > 100 * 1024 * 1024:
                return render(request, 'upload.html', {'message': 'File is too big!'})
            if file.name.endswith((".mp4", ".avi", ".mov")):
                print('video received!, description:', description)
                Media.objects.create(owner=user, reposter=user, media=file, description=description, upload_date=datetime.datetime.now().replace(microsecond=0))
            elif file.name.endswith((".jpg", ".png", ".jpeg")):
                print('image received!, description:', description)
                Media.objects.create(owner=user, reposter=user, media=file, description=description, upload_date=datetime.datetime.now().replace(microsecond=0))
            else:
                return render(request, 'upload.html', {'message': 'Incorrect format!'})
        elif len(description) != 0:
                Media.objects.create(owner=user, reposter=user, description=description, upload_date=datetime.datetime.now().replace(microsecond=0))
                print('have description only!')
        else:
            print('nothing received!')
        return redirect('/')
    else:
        return render(request, 'upload.html', {})
    

# Helper functions:
def collector(request, medias):
    liked_by_user = []
    comments = []
    date = []
    media_parts = []
    shared = []
    if medias is not None:
        for media in medias:
            if Like.objects.filter(user=request.user, liked_media=media).exists():
                liked_by_user.append(1)
            else:
                liked_by_user.append(0)
            if Comment.objects.filter(media=media).exists():
                comments.append((Comment.objects.filter(media=media).order_by('-comment_date')))
            else:
                comments.append(None)
            if Shared.objects.filter(user=request.user, media=media).exists():
                shared.append(1)
            else:
                shared.append(0)
            date.append(media.upload_date.strftime("%Y-%m-%d %H:%M:%S%z"))
            media_parts.append(media)
    
    return zip(media_parts, liked_by_user, comments, shared, date)
