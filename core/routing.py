from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/group_chat/(?P<group_id>[^/]+)/$', consumers.GroupChatConsumer.as_asgi()),
] 