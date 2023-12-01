import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from .models import ChatRoom, Message, PrivateMessage, PrivateChatRoom

from users.models import CustomUser

from channels.exceptions import StopConsumer

import base64, binascii
from django.core.files.base import ContentFile


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None
        self.user_inbox = None

    # Called on connection.
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.room = ChatRoom.objects.get(name=self.room_name)
        self.user = self.scope["user"]
        self.user_inbox = f"inbox_{self.user.username}"

        # Accepts the WebSocket connection.
        self.accept()

        # Joins the room group.
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        # Display the user list to the newly joined user.
        self.send(
            json.dumps(
                {
                    "type": "user_list",
                    "users": [user.username for user in self.room.online.all()],
                }
            )
        )

        if self.user.is_authenticated:
            # Adds the user to the user_inbox group on connect.
            async_to_sync(self.channel_layer.group_add)(
                self.user_inbox,
                self.channel_name,
            )

            # Sends the join event to the chatroom.
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "user_join",
                    "user": self.user.username,
                },
            )
            self.room.online.add(self.user)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

        if self.user.is_authenticated:
            # Removes user from user_inbox group on disconnect.
            async_to_sync(self.channel_layer.group_add)(
                self.user_inbox,
                self.channel_name,
            )

            # Sends the leave event to the chatroom.
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "user_leave",
                    "user": self.user.username,
                },
            )
            self.room.online.remove(self.user)
            raise StopConsumer()

        # When the socket disconnects.

    # Data is parsed to json and message is extracted
    # Message is forwarded using group send to chat message.
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if not self.user.is_authenticated:
            return
        if "file" in text_data_json["message"]:
            # Save the file to the server
            file_data = text_data_json["message"]["file"]
            self.save_file(file_data)

        else:
            message = text_data_json["message"]
            # Handle regular text messages
            self.save_message(message, 0)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "user": self.user.username,
                    "type": "chat_message",
                    "message": message,
                },
            )

    def save_file(self, file_content):
        saved_message = self.save_message(None, 1)
        content = file_content["content"].split(",")

        try:
            image_content = base64.b64decode(content[1])
        except binascii.Error as e:
            # Handle the error, log it, and potentially return an error response
            print(f"Error decoding base64: {e}")
            return
        file_name = f"{saved_message.id}.{file_content['type'].split('/')[-1]}"
        saved_message.image.save(file_name, ContentFile(image_content), save=False)
        saved_message.save()

        # Broadcast file details to the chat room
        self.send(
            json.dumps(
                {
                    "type": "file",
                    "file": {
                        "id": saved_message.id,
                        "filename": file_name,
                        "uploader": self.user.username,
                        "timestamp": str(saved_message.timestamp),
                    },
                }
            )
        )

    def save_message(self, message, is_media):
        saved_message = Message.objects.create(
            user=self.user, room=self.room, content=message, is_media=is_media
        )

        saved_message.save()
        return saved_message

    # Methods for message types for the channel layer.

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def user_join(self, event):
        self.send(text_data=json.dumps(event))

    def user_leave(self, event):
        self.send(text_data=json.dumps(event))

    def private_message(self, event):
        self.send(text_data=json.dumps(event))

    def private_message_delivered(self, event):
        self.send(text_data=json.dumps(event))


# Consumer for Direct Chatting.


class DirectChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.other_username = None
        self.other_user = None

        self.room_name = None
        self.room_group_name = None
        self.room = None

    # Called on connection.
    def connect(self):
        # Initialize attributes properly based on available info.
        # Room info must be made unique for each pair of users.
        self.room_name = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = f"chat_{self.room_name}"
        self.room = PrivateChatRoom.objects.get(pk=self.room_name)
        self.user = self.scope["user"]

        # If the chat initiator, other user object is equal to the receiver
        if self.user == self.room.user1:
            self.other_user = CustomUser.objects.get(pk=self.room.user2.pk)
        # Else Other user object was the initiator.
        else:
            self.other_user = CustomUser.objects.get(pk=self.room.user1.pk)

        # Accepts the WebSocket connection.
        self.accept()

        # Joins the room group.
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        print(f"[{self.channel_name}] - You are now Connected.")

        # Display the user list to the newly joined user.
        self.send(
            json.dumps(
                {
                    "type": "user_list",
                    "users": [user.username for user in self.room.online.all()],
                }
            )
        )

        if self.user.is_authenticated:
            # Sends the join event to the chatroom.
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "user_join",
                    "user": self.user.username,
                },
            )
            self.room.online.add(self.user)

    def disconnect(self, close_code):
        self.room = PrivateChatRoom.objects.get(pk=self.room_name)

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

        if self.user.is_authenticated:
            # Sends the leave event to the chatroom.
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "user_leave",
                    "user": self.user.username,
                },
            )
            self.room.online.remove(self.user)

        # When the socket disconnects.
        print("websocket disconnected...", close_code)
        raise StopConsumer()

    # Json format data is parsed and message is extracted
    # Message is forwarded using group send to chat message.
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if not self.user.is_authenticated:
            return
        if "file" in text_data_json["message"]:
            # Save the file to the server
            file_data = text_data_json["message"]["file"]
            self.save_file(file_data)

        else:
            message = text_data_json["message"]
            # Handle regular text messages
            self.save_message(message, 0)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "user": self.user.username,
                    "type": "chat_message",
                    "message": message,
                },
            )

    def save_file(self, file_content):
        saved_message = self.save_message(None, 1)
        content = file_content["content"].split(",")

        try:
            image_content = base64.b64decode(content[1])
        except binascii.Error as e:
            # Handle the error, log it, and potentially return an error response
            print(f"Error decoding base64: {e}")
            return
        file_name = f"{saved_message.id}.{file_content['type'].split('/')[-1]}"
        saved_message.image.save(file_name, ContentFile(image_content), save=False)
        saved_message.save()

        # Broadcast file details to the chat room
        self.send(
            json.dumps(
                {
                    "type": "file",
                    "file": {
                        "id": saved_message.id,
                        "filename": file_name,
                        "uploader": self.user.username,
                        "timestamp": str(saved_message.timestamp),
                    },
                }
            )
        )

    def save_message(self, message, is_media):
        saved_message = PrivateMessage.objects.create(
            private_sender=self.user,
            private_receiver=self.other_user,
            privateroom=self.room,
            content=message,
            is_media=is_media,
        )

        saved_message.save()
        return saved_message

    # Methods for message types for the channel layer.
    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def user_join(self, event):
        self.send(text_data=json.dumps(event))

    def user_leave(self, event):
        self.send(text_data=json.dumps(event))
