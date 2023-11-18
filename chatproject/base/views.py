import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.urls import reverse
from .models import Friend, Message, Media, Shared, Like, Comment, Requests, ProfileInfo
from django.db.models import Q
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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
    if request.user.is_authenticated is False and request.method == 'POST':
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
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'login.html', {})

def register(request):
    print(request.user.is_authenticated, request.method)
    if request.user.is_authenticated is False and request.method == 'POST':
        print('success')
        name = request.POST['name'].strip()
        surname = request.POST['surname'].strip()
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        file = None
        found = False
        if password != password2 or ' ' in password:
            messages.info(request, 'Passwords did not match or contains spaces')
            found = True
        if is_valid_email(email) is False:
            messages.info(request, 'Invalid email or contains spaces!')
            found = True
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email already registered')
            found = True
        if len(name) == 0:
            messages.info(request, 'Name is empty!')
            found = True
        if len(surname) == 0:
            messages.info(request, 'Surname is empty!')
            found = True
        if ' ' in username:
            messages.info(request, 'Username should not contain spaces!')
            found = True
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username already exists')
            found = True
        if len(request.FILES) == 1:
            file = request.FILES['inputFile']
            if file.name.endswith((".jpg", ".png", ".jpeg")) is False:
                messages.info(request, 'Profile Image is not supported upload one of the followings: jpg, png, jpeg')
                found = True
        if found:
            return redirect('register')
        else:
            user = User.objects.create_user(username=username, email=email,password=password, first_name=name, last_name=surname)
            if file is not None:
                ProfileInfo.objects.create(user=user, profile_image=file)
            else:
                ProfileInfo.objects.create(user=user)
            user.save()
            return redirect('/')
    else:
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'register.html', {})


def chat(request, room):
    print('chat!')
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
        if Friend.objects.filter(user1=current_user, user2=current_recipient).exists() is False or Friend.objects.filter(user1=current_recipient, user2=current_user).exists() is False:
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

def requests(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            print(request.POST['from_user'])
            print(request.POST['command'])
            from_user = User.objects.get(username=request.POST['from_user'])
            if (request.POST['command'] == 'add'):
                Friend.objects.create(user1=request.user, user2=from_user)
            else:
               Friend.objects.get(user1=from_user, user2=request.user).delete()
            Requests.objects.get(from_user=from_user).delete()
            return redirect('requests')
        else:
            request_db = Requests.objects.filter(to_user=request.user)
            return render(request, 'requests.html', {"requests": request_db})
    else:
        return redirect('/')


def profile(request, username):
    if username == 'admin':
        return redirect('/')
    if User.objects.filter(username=username).exists() is False:
        return redirect('/')
    profile_user = User.objects.get(username=username)
    current_user = request.user
    if request.user.is_authenticated:
        if request.method == 'POST':
            friendship1 = Friend.objects.filter(user1=current_user, user2=profile_user)
            friendship2 = Friend.objects.filter(user1=profile_user, user2=current_user)
            print('post')
            if request.POST.get('button_action') == 'add_friend':
                Friend.objects.create(user1=current_user, user2=profile_user)
                return redirect('profile')
            elif request.POST.get('button_action') == 'remove_friend':
                print('removing friend from friendlist')
                if friendship1.exists():
                    friendship1.first().delete()
                if friendship2.exists():
                    friendship2.first().delete()
                return redirect('profile')
            elif request.POST.get('button_action') == 'write_message':
                print('redirecting to chat page')
                if username < request.user.username:
                    return redirect('chat', (username + '-' + current_user.username))
                else:
                    return redirect('chat', (current_user.username + '-' + username))
            else:
                email = request.POST['email'].strip()
                workplace = request.POST['workplace'].strip()
                degree = request.POST['degree'].strip()
                address = request.POST['address'].strip()
                age = request.POST['age'].strip()
                data_dict = {'email': email,
                'workplace': workplace, 'degree': degree,
                'address': address, 'age': age}
                if validator(request, data_dict):
                    print('validate profile infos')
                    profile_info = ProfileInfo.objects.get(user=profile_user)
                    if len(request.FILES) == 1:
                        file = request.FILES['inputFile']
                        if file.name.endswith((".jpg", ".png", ".jpeg")):
                            profile_info.profile_image = file
                        else:
                            return redirect('/')
                    profile_info.degree = degree
                    profile_user.email = email
                    profile_info.workplace = workplace
                    profile_info.address = address
                    print(age)
                    if age != '':
                        profile_info.age = int(age)
                    else:
                        profile_info.age = None
                    profile_info.save()
            return redirect('profile', username)
        else:
            current = False
            friend = 0
            if request.user.username == profile_user.username:
                current = True
            if Friend.objects.filter(user1=request.user, user2=profile_user).exists() and Friend.objects.filter(user1=profile_user, user2=request.user).exists():
                friend = 2
            elif Friend.objects.filter(user1=request.user, user2=profile_user).exists() and Friend.objects.filter(user1=profile_user, user2=request.user).exists() is False:
                friend = 1
            print('get')
            return render(request, 'profile.html',
            {'user': profile_user, 'current': current, 'friend': friend})
    return redirect('/')

def people(request):
    if request.user.is_authenticated:
        peoples = User.objects.all()[:8]
        if request.method == 'POST':
            print('people', request.POST['command'])
            if request.POST['command'] == 'search':
                peoples = User.objects.filter(username__startswith=request.POST['search_handle'])
            elif request.POST['command'] == 'add_friend':
                other_user = User.objects.get(username=request.POST['user'])
                if Friend.objects.filter(user1=request.user, user2=other_user).exists() is False:
                    Friend.objects.create(user1=request.user, user2=other_user)
                if Requests.objects.filter(from_user=request.user, to_user=other_user).exists() is False:
                    Requests.objects.create(from_user=request.user, to_user=other_user)
            elif request.POST['command'] == 'accept_friend':
                other_user = User.objects.get(username=request.POST['user'])
                if Requests.objects.filter(from_user=other_user, to_user=request.user).exists():
                    Requests.objects.filter(from_user=other_user, to_user=request.user).first().delete()
                if Friend.objects.filter(user1=request.user, user2=other_user).exists() is False:
                    Friend.objects.create(user1=request.user, user2=other_user)
            elif request.POST['command'] == 'delete_request':
                # Deletes all relations they have!
                other_user = User.objects.get(username=request.POST['user'])
                if Requests.objects.filter(from_user=other_user, to_user=request.user).exists():
                    Requests.objects.filter(from_user=other_user, to_user=request.user).first().delete()
                if Requests.objects.filter(from_user=request.user, to_user=other_user).exists():
                    Requests.objects.filter(from_user=request.user, to_user=other_user).first().delete()
                if Friend.objects.filter(user1=request.user, user2=other_user).exists():
                    Friend.objects.filter(user1=request.user, user2=other_user).first().delete()
                if Friend.objects.filter(user1=other_user, user2=request.user).exists():
                    Friend.objects.filter(user1=other_user, user2=request.user).first().delete()
            else:
                other_user = User.objects.get(username=request.POST['user'])
                if other_user.username < request.user.username:
                    return redirect('chat', (other_user.username + '-' + request.user.username))
                else:
                    return redirect('chat', (request.user.username + '-' + other_user.username))
            print('people rendering')
            friendship = get_relationships(request.user, peoples)
            return render(request, 'people.html', {'user_and_friendship': zip(peoples,friendship)})
        friendship = get_relationships(request.user, peoples)
        return render(request, 'people.html', {'user_and_friendship': zip(peoples,friendship)})
    else:
        return redirect('/')


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

def validator(request, data_dict):
    found = False
    for key, value in data_dict.items():
        if key == 'email' and is_valid_email(value) is False:
            messages.info(request, 'Invalid email!')
            found = True
        if value != '' and key == 'age' and value.isdigit() == False:
            messages.info(request, 'Age is not numeric')
            found = True
        if len(value) > 100:
            messages.info(request, key.capitalize() + ' too long (max 100)!')
            found = True

    if found:
        return False
    return True

def is_valid_email(email):


    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
    
def get_relationships(current_user, peoples):
    friend_type = []
    for people in peoples:
        relation1 = Friend.objects.filter(user1=current_user, user2=people)
        relation2 = Friend.objects.filter(user1=people, user2=current_user)
        if relation1.exists() and relation2.exists():
            friend_type.append(3)
        elif relation1.exists() is False and relation2.exists():
            friend_type.append(2)
        elif relation1.exists() and relation2.exists() is False:
            friend_type.append(1)
        else:
            friend_type.append(0)
    return friend_type