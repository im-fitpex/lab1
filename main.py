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


