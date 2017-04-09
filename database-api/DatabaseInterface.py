import sqlite3
import os

#TODO: add ability to create database for a user on registration, then raise
#exception if invalid username (i.e.  OS can't name a file after the username)
class DatabaseInterface:
    '''Interface between the program functionality and the database storage of data.'''

    #The name of the table holding contacts
    TABLE_NAME = 'Contacts'

    def __init__(self, username):
        self.__currentUser = str(username)
        self.__dbConnection = None
        self.__dbCursor = None

    def __enter__(self):
        self.Connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.CloseOut()
    
    @property
    def CurrentUser(self):
        return self.__currentUser

    @property
    def Contacts(self):
        return [x for x in self.__dbCursor.execute('select * from ' + DatabaseInterface.TABLE_NAME)]

    def Connect(self):
        '''Connect to the database for the current user'''
        path = os.path.join(os.getcwd(), 'data')
        os.makedirs(path, exist_ok=True)
        self.__dbConnection = sqlite3.connect(os.path.join(path, self.__currentUser + '.db'))
        self.__dbCursor = self.__dbConnection.cursor()
        self.__dbCursor.execute('''create table if not exists %s (
        FirstName text, 
        LastName text, 
        Phone int, 
        Email text, 
        Address text
        )''' % DatabaseInterface.TABLE_NAME)

    def Commit(self):
        '''Commit changes to the database.
        Not strictly necessary, as all changes will be committed
        when Closing Out, but this function is here if you need it.'''
        if self.__dbConnection:
            self.__dbConnection.commit()

    def Close(self):
        '''Close the database connection without committing.
        Not for the faint of heart.'''
        self.__dbConnection.close()

    def CloseOut(self):
        '''Commit changes and close the database connection'''
        if self.__dbConnection:
            self.Commit()
            self.Close()

    def AddContact(self, contact):
        '''Add contact into the current user's database'''
        self.__dbConnection.execute()

if __name__ == '__main__':
    #Example 1: With with statement
    with DatabaseInterface('mason11') as db:
        print(db.Contacts)

    #Example 2: The dirty way
    #db = DatabaseInterface('mason11')
    #db.Connect()
    #print(db.CurrentUser)
    #db.CloseOut()