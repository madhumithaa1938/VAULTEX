
from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, user_id, username, email, password_hash):

        self.id = str(user_id)
        self.username = username
        self.email = email
        self.password_hash = password_hash
