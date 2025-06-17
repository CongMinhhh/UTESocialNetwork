import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, Profile, GroupMessage, Group
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Get the user from the scope
            self.user = self.scope["user"]
            
            # Check if user is authenticated
            if isinstance(self.user, AnonymousUser):
                logger.warning("Unauthenticated user attempted to connect")
                await self.close()
                return

            # Create a unique room name for each user pair
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"WebSocket connection established for user {self.user.username} in room {self.room_name}")
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"WebSocket connection closed for user {self.user.username} with code {close_code}")
        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            receiver_id = text_data_json['receiver_id']

            # Save message to database
            await self.save_message(message, receiver_id)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                    'sender_profile_img': await self.get_user_profile_image(self.user),
                }
            )
            logger.info(f"Message sent from {self.user.username} to room {self.room_name}")
        except json.JSONDecodeError:
            logger.error("Invalid JSON data received")
            await self.send(text_data=json.dumps({
                'error': 'Invalid message format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to process message'
            }))

    async def chat_message(self, event):
        try:
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'sender_id': event['sender_id'],
                'sender_username': event['sender_username'],
                'sender_profile_img': event['sender_profile_img'],
            }))
            logger.info(f"Message broadcasted in room {self.room_name}")
        except Exception as e:
            logger.error(f"Error in chat_message: {str(e)}")

    @database_sync_to_async
    def save_message(self, message, receiver_id):
        try:
            receiver = User.objects.get(id=receiver_id)
            Message.objects.create(
                sender=self.user,
                receiver=receiver,
                content=message
            )
            logger.info(f"Message saved to database from {self.user.username} to {receiver.username}")
        except User.DoesNotExist:
            logger.error(f"Receiver user {receiver_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            raise

    @database_sync_to_async
    def get_user_profile_image(self, user):
        try:
            profile = Profile.objects.get(user=user)
            return profile.profileimg.url
        except Profile.DoesNotExist:
            return '/media/profile_images/blank-profile-picture.png'

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'group_{self.group_id}'
        self.user = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            group_id = text_data_json['group_id']

            # Save message to database
            await self.save_group_message(message, group_id)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'group_chat_message',
                    'message': message,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                    'sender_profile_img': await self.get_user_profile_image(self.user),
                }
            )
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to process message'
            }))

    async def group_chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'sender_profile_img': event['sender_profile_img'],
        }))

    async def save_group_message(self, message, group_id):
        group = await database_sync_to_async(Group.objects.get)(id=group_id)
        group_message = await database_sync_to_async(GroupMessage.objects.create)(
            group=group,
            sender=self.user,
            content=message
        )
        return group_message

    async def get_user_profile_image(self, user):
        try:
            profile = await database_sync_to_async(Profile.objects.get)(user=user)
            return profile.profileimg.url if profile.profileimg else None
        except Profile.DoesNotExist:
            return None 