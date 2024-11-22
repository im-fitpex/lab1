class User:
    def __init__(self, user_id, username, email, status="offline"):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.status = status
        self.contacts = []

    def add_contact(self, contact):
        if contact not in self.contacts:
            self.contacts.append(contact)

    def change_status(self, status):
        self.status = status


class Message:
    def __init__(self, message_id, sender, recipient, content, timestamp, is_read=False):
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
    def __init__(self, chat_id, participants, group_name):
        super().__init__(chat_id, participants)
        self.group_name = group_name

    def add_participant(self, user):
        if user not in self.participants:
            self.participants.append(user)

    def remove_participant(self, user):
        if user in self.participants:
            self.participants.remove(user)


