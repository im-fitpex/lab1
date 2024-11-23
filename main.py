import json


# Класс для работы с JSON
class DataStore:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load()

    def load(self):
        # Загрузка данных из JSON-файла.
        with open(self.file_path, "r") as file:
            return json.load(file)

    def save(self):
        # Сохранение данных в JSON-файл.
        with open(self.file_path, "w") as file:
            json.dump(self.data, file, indent=4)

    def get_user(self, user_id):
        # Получение пользователя по ID.
        return next(
            (user for user in self.data["users"] if user["user_id"] == user_id), None
        )

    def update_user(self, user):
        # Обновление данных пользователя.
        for stored_user in self.data["users"]:
            if stored_user["user_id"] == user.user_id:
                stored_user.update(
                    {
                        "username": user.username,
                        "email": user.email,
                        "chats": [chat.chat_id for chat in user.chats],
                    }
                )
                break
        self.save()

    def update_chat(self, chat):
        # Обновление данных чата.
        for stored_chat in self.data["chats"]:
            if stored_chat["chat_id"] == chat.chat_id:
                stored_chat["messages"] = [
                    {
                        "message_id": message.message_id,
                        "sender_id": message.sender.user_id,
                        "content": message.content,
                    }
                    for message in chat.messages
                ]
                break
        self.save()


# Кастомные исключения
class MessengerException(Exception):
    pass


class UserNotFoundException(MessengerException):
    pass


class InvalidMessageException(MessengerException):
    pass


# Основные классы
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
    def __init__(self, message_id, sender, content):
        self.message_id = message_id
        self.sender = sender
        self.content = content


class Chat:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)


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
    def __init__(self, message_id, sender, content, attachment):
        super().__init__(message_id, sender, content)
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


# Основная функция
def main():
    # Инициализация хранилища
    data_store = DataStore("example.json")

    # Загрузка пользователя
    user_data = data_store.get_user(1)
    if not user_data:
        raise UserNotFoundException("User not found in JSON.")

    user = User(user_data["user_id"], user_data["username"], user_data["email"])

    # Загрузка чатов
    chats = []
    for chat_data in data_store.data["chats"]:
        chat = Chat(chat_data["chat_id"])
        for message_data in chat_data["messages"]:
            sender = user if message_data["sender_id"] == user.user_id else None
            chat.add_message(
                Message(message_data["message_id"], sender, message_data["content"])
            )
        chats.append(chat)

    # Добавление пользователя в чат
    chat = chats[0]
    user.join_chat(chat)

    # Пример изменения данных
    user.username = "new_username"
    data_store.update_user(user)

    # Пример отправки сообщения
    user.send_message(chat, "Updated message!")
    data_store.update_chat(chat)

    print("JSON успешно обновлён!")


# Начало программы
if __name__ == "__main__":
    main()
