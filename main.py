import json
import xml.etree.ElementTree as ET


# Общие исключения
class MessengerException(Exception):
    pass


class UserNotFoundException(MessengerException):
    pass


class InvalidMessageException(MessengerException):
    pass


# Модели данных
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
    def __init__(self, message_id, sender, content, is_read=False):
        self.message_id = message_id
        self.sender = sender
        self.content = content
        self.is_read = is_read

    def mark_as_read(self):
        self.is_read = True


class Chat:
    def __init__(self, chat_id):
        self.chat_id = chat_id
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
    def __init__(self, notification_id, user, message, is_seen=False):
        self.notification_id = notification_id
        self.user = user
        self.message = message
        self.is_seen = is_seen

    def mark_as_seen(self):
        self.is_seen = True


class Reaction:
    def __init__(self, message_id, user, reaction_type):
        self.message_id = message_id
        self.user = user
        self.reaction_type = reaction_type


class MediaMessage(Message):
    def __init__(self, message_id, sender, content, attachment):
        super().__init__(message_id, sender, content)
        self.attachment = attachment


class Authentication:
    def __init__(self):
        self.logged_in_users = {}

    def login(self, user, password):
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


# Работа с JSON
class DataStore:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load()

    def load(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def save(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def get_user(self, user_id):
        return next((user for user in self.data["users"] if user["user_id"] == user_id), None)

    def update_user(self, user):
        for stored_user in self.data["users"]:
            if stored_user["user_id"] == user.user_id:
                stored_user.update({
                    "username": user.username,
                    "email": user.email,
                    "chats": [chat.chat_id for chat in user.chats]
                })
                break
        self.save()

    def update_chat(self, chat):
        for stored_chat in self.data["chats"]:
            if stored_chat["chat_id"] == chat.chat_id:
                stored_chat["messages"] = [
                    {
                        "message_id": message.message_id,
                        "sender_id": message.sender.user_id,
                        "content": message.content
                    }
                    for message in chat.messages
                ]
                break
        self.save()


# Работа с XML
class XMLDataStore:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()

    def save(self):
        self.tree.write(self.file_path, encoding="utf-8", xml_declaration=True)

    def get_user(self, user_id):
        user_elem = self.root.find(f"./users/user[@id='{user_id}']")
        if user_elem is None:
            return None
        return {
            "user_id": int(user_elem.get("id")),
            "username": user_elem.find("username").text,
            "email": user_elem.find("email").text,
            "chats": [
                int(chat_elem.text) for chat_elem in user_elem.find("chats")
            ]
        }

    def update_user(self, user):
        user_elem = self.root.find(f"./users/user[@id='{user.user_id}']")
        if user_elem is not None:
            user_elem.find("username").text = user.username
            user_elem.find("email").text = user.email
            chats_elem = user_elem.find("chats")
            chats_elem.clear()
            for chat in user.chats:
                ET.SubElement(chats_elem, "chat").text = str(chat.chat_id)
        self.save()

    def get_chat(self, chat_id):
        chat_elem = self.root.find(f"./chats/chat[@id='{chat_id}']")
        if chat_elem is None:
            return None
        return {
            "chat_id": int(chat_elem.get("id")),
            "messages": [
                {
                    "message_id": int(msg_elem.get("id")),
                    "sender_id": int(msg_elem.find("sender_id").text),
                    "content": msg_elem.find("content").text,
                }
                for msg_elem in chat_elem.find("messages")
            ],
        }

    def update_chat(self, chat):
        chat_elem = self.root.find(f"./chats/chat[@id='{chat.chat_id}']")
        if chat_elem is not None:
            messages_elem = chat_elem.find("messages")
            messages_elem.clear()
            for message in chat.messages:
                msg_elem = ET.SubElement(messages_elem, "message", id=str(message.message_id))
                ET.SubElement(msg_elem, "sender_id").text = str(message.sender.user_id)
                ET.SubElement(msg_elem, "content").text = message.content
        self.save()


# Основной код
def main():
    json_store = DataStore("db.json")
    xml_store = XMLDataStore("db.xml")
    # Пример взаимодействия с json
    json_user_data = json_store.get_user(1)
    json_user = User(json_user_data["user_id"], json_user_data["username"], json_user_data["email"])
    json_user.username = "Updated_JSON_User"
    json_store.update_user(json_user)
    # Пример взаимодействия с xml
    xml_user_data = xml_store.get_user(1)
    xml_user = User(xml_user_data["user_id"], xml_user_data["username"], xml_user_data["email"])
    xml_user.username = "Updated_XML_User"
    xml_store.update_user(xml_user)

    print("Данные обновлены!")


if __name__ == "__main__":
    main()
