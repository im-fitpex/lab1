import json
import xml.etree.ElementTree as ET

# Custom exceptions
class MessengerException(Exception):
    pass


class UserNotFoundException(MessengerException):
    pass


class InvalidMessageException(MessengerException):
    pass


class User:
    def __init__(self, user_id, username, email):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.chats = []

    def join_chat(self, chat):
        if chat not in self.chats:
            self.chats.append(chat)
        else:
            raise MessengerException("User is already in this chat.")

    def send_message(self, chat, content):
        if chat not in self.chats:
            raise UserNotFoundException("User is not a member of this chat.")
        if not content.strip():
            raise InvalidMessageException("Message content cannot be empty.")
        chat.add_message(Message(len(chat.messages) + 1, self, content))


class Message:
    def __init__(
        self, message_id, sender, recipient, content, timestamp, is_read=False
    ):
        self.message_id = message_id
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.timestamp = timestamp
        self.is_read = is_read

    def mark_as_read(self):
        self.is_read = True


class Chat:
    def __init__(self, chat_id, participants):
        self.chat_id = chat_id
        self.participants = participants
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)

    def get_last_message(self):
        return self.messages[-1] if self.messages else None


class GroupChat(Chat):
    def __init__(self, chat_id, group_name):
        super().__init__(chat_id)
        self.group_name = group_name
        self.participants = []

    def add_participant(self, user):
        if user not in self.participants:
            self.participants.append(user)
        else:
            raise MessengerException("User is already in this group.")

    def remove_participant(self, user):
        if user in self.participants:
            self.participants.remove(user)
        else:
            raise UserNotFoundException("User not found in the group.")


class Attachment:
    def __init__(self, file_name, file_size, file_type, uploaded_by):
        self.file_name = file_name
        self.file_size = file_size
        self.file_type = file_type
        self.uploaded_by = uploaded_by


class Notification:
    def __init__(self, notification_id, user, message, timestamp, is_seen=False):
        self.notification_id = notification_id
        self.user = user
        self.message = message
        self.timestamp = timestamp
        self.is_seen = is_seen

    def mark_as_seen(self):
        self.is_seen = True


class Reaction:
    def __init__(self, message_id, user, reaction_type):
        self.message_id = message_id
        self.user = user
        self.reaction_type = reaction_type


class MediaMessage(Message):
    def __init__(self, message_id, sender, recipient, content, timestamp, attachment):
        super().__init__(message_id, sender, recipient, content, timestamp)
        self.attachment = attachment


class Authentication:
    def __init__(self):
        self.logged_in_users = {}

    def login(self, user, password):
        # Simplified example
        self.logged_in_users[user.user_id] = True

    def logout(self, user):
        if user.user_id in self.logged_in_users:
            del self.logged_in_users[user.user_id]


class Settings:
    def __init__(self, user):
        self.user = user
        self.preferences = {}

    def update_preference(self, key, value):
        self.preferences[key] = value

    def change_username(self, new_username):
        self.user.username = new_username
