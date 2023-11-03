from django.urls import path 
  
from . import consumers 
  
websocket_urlpatterns = [ 
    path('ws/<str:room>/', consumers.Chat.as_asgi()),
] 