from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    current_user = request.user
    user_name = current_user.username
    return render(request, 'index.html', {'user': current_user, 'user_name': user_name})