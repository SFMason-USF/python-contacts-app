import sqlite3
import os

#TODO: add ability to create database for a user on registration, then raise
#exception if invalid username (i.e.  OS can't name a file after the username)
class DatabaseInterface:
    '''Interface between the program functionality and the database storage of data.
    Allows connections to multiple databases from one instance, but it is intended to 
    maintin 1 database connection '''

    TABLE_NAME = 'Contacts'

    def __init__(self, username):
        self.__currentUser = str(username)
        self.__dbConnection = None

    def __enter__(self):
        self.Connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.CloseOut()
    
    @property
    def CurrentUser(self):
        return self.__currentUser

    @CurrentUser.setter
    def CurrentUser(self, newUser):
        #TODO: Later if validation is necessary, validate
        self.__currentUser = str(newUser)

    def Connect(self):
        '''Connect to the database for the current user'''
        path = os.path.join(os.getcwd(), 'data')
        os.makedirs(path, exist_ok=True)
        self.__dbConnection = sqlite3.connect(os.path.join(path, self.__currentUser + '.db'))
        self.__dbConnection.execute('''SELECT ? FROM sqlite_master WHERE tpe='table' AND name=?''', ())

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
        print(db.CurrentUser)

    #Example 2: The dirty way
    db = DatabaseInterface('mason11')
    db.Connect()
    print(db.CurrentUser)
    db.CloseOut()