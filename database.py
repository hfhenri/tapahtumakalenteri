
import sqlite3
from werkzeug.security import check_password_hash
import uuid

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

    def get_image(self, image_id):
        result = self.query("""
        SELECT ImageData FROM EventImages 
        WHERE ImageID = ?""", [image_id])

        return result
    
    def add_image(self, data):
        image_id = str(uuid.uuid4())
        self.execute("""
        INSERT INTO EventImages (ImageID, ImageData)
        VALUES (?, ?)""", [image_id, data])
    
        return image_id

    def get_event(self, event_id):
        return self.query("""
        SELECT UserID, Title, Description, Price, CategoryID, ImageID, Date, ShortDescription
        FROM Events
        WHERE EventID = ?""", [event_id])
    
    def delete_event(self, event_id):
        self.execute("DELETE FROM Events WHERE EventID = ?", [event_id])

    def update_event(self, event_id, title, description, short_description, price, category_id, image_id, event_date):
        self.execute("""
            UPDATE Events
            SET Title = ?, Description = ?, ShortDescription = ?, Price = ?, CategoryID = ?, ImageID = ?, Date = ?
            WHERE EventID = ?""", [title, description, short_description, price, category_id, image_id, event_date, event_id])


    def add_event(self, user_id, title, short_description, description, price, category_id, image_id, event_date):
        event_id = str(uuid.uuid4())
        self.execute("""
        INSERT INTO Events (UserID, Title, ShortDescription, Description, Price, CategoryID, ImageID, EventID, Date) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", [str(user_id), title, short_description, description, price, category_id, image_id, event_id, event_date])

    def get_all_events(self):
        return self.query("""
        SELECT Title, ShortDescription, Price, ImageID, EventID, Date FROM Events""")

    def add_question(self, event_id, user_id, question_text):
        
        question_id = str(uuid.uuid4())
        self.execute("""
        INSERT INTO Questions (QuestionID, EventID, UserID, QuestionText)
        VALUES (?, ?, ?, ?)""", [question_id, event_id, user_id, question_text])

    def get_user_events(self, user_id):
       
        return self.query("""
        SELECT Title, ShortDescription, Price, ImageID, EventID, Date FROM Events WHERE UserID = ?""", [user_id])
    
    def search_events(self, keyword):
       
        return self.query("""
        SELECT Title, ShortDescription, Price, ImageID, EventID, Date FROM Events 
        WHERE Title LIKE ? OR Description LIKE ?""", [f"%{keyword}%", f"%{keyword}%"])

    def get_event_questions(self, event_id):
        
        return self.query("""
        SELECT Questions.QuestionID, Questions.QuestionText, Users.Username 
        FROM Questions
        JOIN Users ON Questions.UserID = Users.UserID 
        WHERE Questions.EventID = ?""", [event_id])


