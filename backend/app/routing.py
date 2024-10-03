from django.urls import re_path
from app import consumers

websocket_urlpatterns = [
    re_path(r'ws/chatroom/$', consumers.ChatroomConsumer.as_asgi()),
    re_path(r'ws/game/$', consumers.GameConsumer.as_asgi()),
    re_path(r'ws/tournament/$', consumers.TournamentConsumer.as_asgi()),
]