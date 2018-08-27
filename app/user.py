class User:

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def obj_to_dict(self):
        user_dict = dict()
        user_dict['id'] = self.id
        user_dict['username'] = self.username
        user_dict['password'] = self.password
