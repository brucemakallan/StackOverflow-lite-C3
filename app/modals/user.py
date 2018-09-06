import psycopg2

from passlib.hash import pbkdf2_sha256 as sha256


class User:

    def __init__(self, user_id, username, full_name, email, password):
        self.id = user_id
        self.username = username
        self.full_name = full_name
        self.email = email
        self.password = password

    def create(self, cur):
        """Create a new row"""
        try:
            sql = """INSERT INTO users(user_username, user_full_name, user_email, user_password) 
                    VALUES(%s, %s, %s, %s) RETURNING user_id"""
            password_hash = sha256.hash(self.password)
            cur.execute(sql, (self.username, self.full_name, self.email, password_hash))
            new_id = cur.fetchone()[0]
            return new_id
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    @staticmethod
    def read_all(cur):
        """Read all rows"""
        try:
            users_list = []
            cur.execute("SELECT user_id, user_username, user_full_name, user_email, user_password FROM users")
            row = cur.fetchone()
            while row is not None:
                user = User(row[0], row[1], row[2], row[3], row[4])
                users_list.append(user)
                row = cur.fetchone()
            return users_list
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    @staticmethod
    def read_one(cur, user_id):
        """Read one row"""
        try:
            user = None
            cur.execute("""SELECT user_id, user_username, user_full_name, user_email, user_password 
                          FROM users WHERE user_id = """ + str(user_id))
            row = cur.fetchone()
            if row is not None:
                user = User(row[0], row[1], row[2], row[3], row[4])
            return user
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def update(self, cur):
        """Update one row"""
        try:
            sql = """UPDATE users SET user_username = %s, user_full_name = %s, user_email = %s, user_password = %s 
                    WHERE user_id = %s"""
            cur.execute(sql, (self.username, self.full_name, self.email, self.password))
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def delete(self, cur):
        """Delete one row"""
        try:
            cur.execute("DELETE FROM users WHERE user_id = %s", (str(self.id),))
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def obj_to_dict(self):
        """Convert object to dictionary (for use as JSON). Don't show password"""
        user_dict = dict()
        user_dict['id'] = self.id
        user_dict['username'] = self.username
        user_dict['full_name'] = self.full_name
        user_dict['email'] = self.email
        return user_dict
