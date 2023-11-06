import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Friend, Message
from django.db.models import Q


def logout(request):
    auth.logout(request)
    return redirect('/')

def index(request):
    current_user = request.user
    user_name = current_user.username
    return render(request, 'index.html', {'user': current_user, 'user_name': user_name})

# TODO: 1) validations to be added! 2) and not logged in only requirement
def login(request):
    if request.method == 'POST':
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
    if request.method == 'POST':
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


# TODO: make only friends chattable! -> DONE
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
        messages = Message.objects.filter(Q(sender=current_user, recipient=current_recipient) | Q(sender=current_recipient,recipient=current_user)).order_by('timestamp')
        friendship = Friend.objects.filter(Q(user1=current_user, user2=current_recipient) | Q(user1=current_recipient,user2=current_user)).last()
        friendship.last_message_date = datetime.datetime.now()
        friendship.save()
        print(friendship.last_message_date)
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