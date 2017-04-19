import sqlite3
import os

class UserAlreadyExistsException(Exception): 
    pass

class UserNotFoundException(Exception):
    pass

class DatabaseNotConnectedException(Exception):
    pass

class DatabaseInterface:
    '''Interface between the program functionality and the database storage of data.'''
    #Names of database columns
    class KEYS:
        FirstName = 'FirstName'
        LastName = 'LastName'
        Phone = 'Phone'
        Email = 'Email'
        Address = 'Address'
        def __iter__(self):
            yield DatabaseInterface.KEYS.FirstName
            yield DatabaseInterface.KEYS.LastName
            yield DatabaseInterface.KEYS.Phone
            yield DatabaseInterface.KEYS.Email
            yield DatabaseInterface.KEYS.Address

    def __init__(self, username):
        self.__currentUser = str(username)
        if self.__currentUser == ':memory:':
            self.__currentUser = 'DEBUG'
        self.__dbConnection = None

    def __enter__(self):
        self.Connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.CloseOut()

    def __rowToContact(self, row):
        return Contact(row[DatabaseInterface.KEYS.FirstName], 
                       row[DatabaseInterface.KEYS.LastName], 
                       row[DatabaseInterface.KEYS.Phone], 
                       row[DatabaseInterface.KEYS.Email], 
                       row[DatabaseInterface.KEYS.Address])
    
    @property
    def CurrentUser(self):
        return self.__currentUser

    @property
    def Contacts(self):
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        return [self.__rowToContact(row) for row in self.__dbConnection.execute('select * from {}'.format(self.__currentUser)).fetchall()]

    @property
    def Users(self):
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        return [row['username'] for row in self.__dbConnection.execute('select username from Users').fetchall()]

    def Connect(self):
        '''Connect to the database for the current user'''
        self.__dbConnection = sqlite3.connect(os.path.join(os.getcwd(), 'contacts.db') 
                                              if self.__currentUser != 'DEBUG' else ':memory:') #debug
        self.__dbConnection.row_factory = sqlite3.Row
        self.__dbConnection.execute('''create table if not exists {} ({} text, {} text, {} int, {} text, {} text)'''
                                    .format(self.__currentUser, *DatabaseInterface.KEYS()))
        self.__dbConnection.execute('''create table if not exists Users (username text PRIMARY KEY, password text)''')

    def UserExists(self):
        '''Returns true if the current user of this database interface exists, false otherwise'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        return 0 != len(self.__dbConnection.execute('''select * from Users where username=?''', (self.__currentUser,)).fetchall())

    def RegisterUser(self, username, password):
        '''Register a new user to the users table. Raises a UserAlreadyExists exception if username already exists'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        if 0 != len(self.__dbConnection.execute('''select * from Users where username=?''', (username,)).fetchall()):
            raise UserAlreadyExistsException()
        self.__dbConnection.execute('''insert into Users (username, password) values (?, ?)''', (username, password))

    def CheckPassword(self, password):
        '''Returns true if the current user exists and his password is password'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        if not self.UserExists():
            return False
        try:
            return self.__dbConnection.execute('''select * from Users where username=? and password=?''', (self.__currentUser, password)).fetchall()[0]['password'] == password
        except IndexError:
            return False

    def Commit(self):
        '''Commit changes to the database.
        Not strictly necessary, as all changes will be committed
        when Closing Out, but this function is here if you need it.'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        if self.__dbConnection:
            self.__dbConnection.commit()

    def Close(self):
        '''Close the database connection without committing.
        Not for the faint of heart.'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        self.__dbConnection.close()

    def CloseOut(self):
        '''Commit changes and close the database connection'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        self.Commit()
        self.Close()

    def AddContact(self, contact):
        '''Add contact into the current user's database'''
        #Check if it's already in
        #I would use unique and primary keys,
        #but we have to check against both first and last name
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        if self.__dbConnection.execute('''select exists(select 1 from {} where {}=? and {}=? limit 1)'''
                                          .format(self.__currentUser, 
                                                  DatabaseInterface.KEYS.FirstName, 
                                                  DatabaseInterface.KEYS.LastName), 
                                          (contact.name.split(' '))).fetchone()[0] == 0:
            name = None
            try:
                name = contact.name.split()
            except AttributeError:
                name = [None, None]
            if len(name) < 2:
                name.append(None)
            self.__dbConnection.execute('''insert into {} ({}, {}, {}, {}, {}) values (?, ?, ?, ?, ?)'''
                                        .format(self.__currentUser, *DatabaseInterface.KEYS()), 
                                        (name[0], 
                                         name[1], 
                                         contact.phone, 
                                         contact.email, 
                                         contact.home))
    def Search(self, searchStr):
        '''Returns a list of contacts that contain searchStr anywhere within any of their columns.
        e.g. Search(813) will return people with 813 phone numbers and people who live on 813 North St.
        Wildcards: % is 0 or more characters; _ is any single character. e.g. Search(8_3) returns numbers with 813 and 863.'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        searchStr = '%' + searchStr + '%'
        return [self.__rowToContact(row) 
                for row in self.__dbConnection.execute('''select * from {} 
                where {} like ? or 
                {} like ? or 
                {} like ? or 
                {} like ? or 
                {} like ?'''
                .format(self.__currentUser, 
                        *DatabaseInterface.KEYS()), 
                [searchStr for i in range(5)]).fetchall()]

    def DeleteContact(self, contact):
        '''Given a contact, deletes contacts with matching fields.'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        name = None
        try:
            name = contact.name.split()
        except AttributeError:
            name = [None, None]
        if len(name) < 2:
            name.append(None)
        self.__dbConnection.execute('delete from {} where {}=? and {}=? and {}=? and {}=? and {}=?'
                                    .format(self.__currentUser, 
                                            *DatabaseInterface.KEYS()), 
                                    (name[0],
                                     name[1],
                                     contact.phone, 
                                     contact.email, 
                                     contact.home))

    def EditContact(self, contact, newContact):
        '''Given a contact, replaces the contact in the database with newContact'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        name = None
        try:
            name = contact.name.split()
        except AttributeError:
            name = [None, None]
        if len(name) < 2:
            name.append(None)
        newName = None
        try:
            newName = newContact.name.split()
        except AttributeError:
            newName = [None, None]
        while len(newName) < 2:
            newName.append(None)

        self.__dbConnection.execute('update {} set {}=?, {}=?, {}=?, {}=?, {}=? where {}=? and {}=?'
                                    .format(self.__currentUser, 
                                            *DatabaseInterface.KEYS(),
                                            *DatabaseInterface.KEYS()), 
                                    (newName[0],
                                     newName[1],
                                     newContact.phone, 
                                     newContact.email, 
                                     newContact.home,
                                     name[0],
                                     name[1]))

if __name__ == '__main__':
    #Example 1: With with statement
    username = 'mason11'
    with DatabaseInterface(username) as db:
        print('Logging in')
        exists = db.UserExists()
        print(exists)
        if not exists:
            db.RegisterUser('mason11', 'pw')
        exists = db.UserExists()
        print(exists)
        print('Attempting login')
        login = db.CheckPassword('pw')
        print(login)
        login = db.CheckPassword(' pw')
        print(login)

        print('Adding contacts')
        db.AddContact(Contact('Spenser', 'Mason', 8139570260, 'mason11@mail.usf.edu', '111 W North St'))
        db.AddContact(Contact('Christian', 'Morales', 8637014768, None, None))
        for contact in db.Contacts:
            print(contact)
        print()

        print('Deleting contact')
        db.DeleteContact(db.Contacts[0])
        for contact in db.Contacts:
            print(contact)
        print()

        print('Editing contact')
        db.EditContact(db.Contacts[0], Contact('Spenser', 'Mason', None, 'mason11', None))
        for contact in db.Contacts:
            print(contact)
        print()
        input('Press enter to continue...')

    #Example 2: The dirty way
    #db = DatabaseInterface(username)
    #db.Connect()
    #db.AddContact(Contact('Spenser', 'Mason', 8139570260, 'mason11@mail.usf.edu', '111 W North St'))
    #db.CloseOut()
