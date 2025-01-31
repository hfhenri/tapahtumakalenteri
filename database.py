
import sqlite3
class Database():

    def __init__(self):
        self.connection = sqlite3.connect("database.db")

    def query(self, sql, params=[]):
        self.connection = sqlite3.connect("database.db")
        result = self.connection.execute(sql, params).fetchall()
        self.connection.commit()
        return result
    
    def execute(self, sql, params=[]):
        self.connection = sqlite3.connect("database.db")
        self.connection.execute(sql, params)
        self.connection.commit()

    def add_user(self, username, password_hash):
        user_id = str(uuid.uuid4())
        self.execute("""
        INSERT INTO Users (UserID, Username, PasswordHash) 
        VALUES (?, ?, ?)""", [user_id, username, password_hash])

    def get_user_id(self, username):
        
        return self.query("""
        SELECT UserID FROM Users WHERE Username = ? """, [username])
    
    def get_username(self, user_id):

        return self.query("""
        SELECT Username FROM Users WHERE UserID = ?""", [user_id])
    
    def check_password(self, username, password):
        db_hash = self.query("""
        SELECT PasswordHash FROM Users WHERE Username = ?""", [username])

        if len(db_hash) == 0:
            return False

        if check_password_hash(db_hash[0][0], password) is False:
            return False
        return True
