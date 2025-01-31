
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
