from config.db import db


class User():

    def __init__(self, first_name, last_name, email, password, username):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = password

    def __str__(self):
        return f" >>>  User({self.username},{self.email},{self.first_name},{self.last_name},{self.password})"

    def __repr__(self):
        rep = 'User(' + self.username + ',' + str(self.email) + ')'
        return rep

    @staticmethod
    def UserExists(query):
        user = db.users.find_one(query)
        if user:
            user['_id'] = str(user['_id'])
            return user
        else:
            return False

    def serialize(self):
        return {
            '_id': str(self._id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'password': self.password,
        }

    def toDictionary(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'password': self.password,
        }

    @staticmethod
    def from_dict(user_dict):
        return User(user_dict['username'], user_dict['password'], user_dict['email'])

    @staticmethod
    def seed():
        db.users.delete_many({})
        user1 = User(
            first_name='alice',
            last_name='stone',
            username='alice',
            password='pakistan123>',
            email='alice@gmail.com'
        )
        user2 = User(
            first_name='bob',
            last_name='stone',
            username='bob',
            password='pakistan123>',
            email='bob@gmail.com'
        )
        user3 = User(
            first_name='carson',
            last_name='stone',
            username='carson',
            password='pakistan123>',
            email='carson@gmail.com'
        )
        user1 = db.users.insert_one(user1.toDictionary())
        user2 = db.users.insert_one(user2.toDictionary())
        user3 = db.users.insert_one(user3.toDictionary())
        users = db.users.find()
        data = []
        for user in users:
            data.append({"_id": str(user["_id"]), "username": user["username"], "first_name": user["first_name"], "last_name": user["last_name"], "email": user["email"]})
        return data
