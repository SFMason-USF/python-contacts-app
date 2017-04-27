# Authors: Christian Morales, Spencer Mason, and Jacob Schoen
from tkinter import *
import sqlite3
import os
import re

###################################Contact Class####################################################
# Exceptions to check inputs when creating a contact
class InvalidContactPhoneException(Exception):
    pass
class InvalidContactEmailException(Exception):
    pass
class InvalidContactAddressException(Exception):
    pass

class Contact:
    def __init__(self, first_name, last_name, phone, email, home_tuple):
        self.name=first_name + " " + last_name
        self.phone=phone
        self.email=email
        # tuple to hold street, city, state, zip
        self.home=home_tuple

    def __str__(self):
        return "Name: {0}\nPhone Number: {1}\nE-mail Address: {2}\nHome Address: {3}".format(self.name,
                                                                                             self.phone,
                                                                                             self.email,
                                                                                             self.home)

    def __repr__(self):
        return str(self)

    # __lt__ used for sorting
    def __lt__(self, other):
        return (self.name, self.phone, self.email, self.home) < (other.name, other.phone, other.email, other.home)

    @property
    def name(self):
        return "{}".format(self.__name)

    @property
    def phone(self):
        return "{}".format(self.__phone)

    @property
    def email(self):
        return "{}".format(self.__email)

    @property
    def home(self):
        return self.__home

    @name.setter
    def name(self, name):
        self.__name=name

    @phone.setter
    def phone(self, phone):
        # regex pattern to take care of acceptable phone numbers
        phonePattern=re.compile('^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$')
        # check if phone matches regex pattern and 10 char
        if phonePattern.match(str(phone)) and len(str(phone))==10:
            self.__phone=phone
        # check if phone entry is empty
        elif not phone:
            self.__phone=phone
        else:
            raise InvalidContactPhoneException

    @email.setter
    def email(self, email):
        # email pattern to check if input matches acceptable email
        emailPattern=re.compile("[^@]+@[^@]+\.[^@]+")
        # check if email matches regex pattern or empty field
        if emailPattern.match(email) or not email:
            self.__email=email
        else:
            raise InvalidContactEmailException

    @home.setter
    def home(self, address_info):
        zipCodePattern = re.compile(r'.*(\d{5}(\-\d{4})?)$')
        # check if every field is completed and zip code matches 5 numbers
        if all(address_info) and zipCodePattern.match(str(address_info[3])) and len(str(address_info[3]))==5:
            self.__home = address_info
        # check if none of the fields are completed
        elif not all(address_info):
            self.__home = address_info
        # if neither, then raise InvalidContactAddressException
        else:
            raise InvalidContactAddressException

##########################DatabaseInterface Class#######################################################################
# Exceptions when working with Database
class UserAlreadyExistsException(Exception):
    pass
class UserNotFoundException(Exception):
    pass
class DatabaseNotConnectedException(Exception):
    pass

class DatabaseInterface:
    '''Interface between the program functionality and the database storage of data.'''
    # Names of database columns
    class KEYS:
        FirstName = 'FirstName'
        LastName = 'LastName'
        Phone = 'Phone'
        Email = 'Email'
        Street = 'Street'
        City = 'City'
        State = 'State'
        Zip = 'Zip'

        def __iter__(self):
            yield DatabaseInterface.KEYS.FirstName
            yield DatabaseInterface.KEYS.LastName
            yield DatabaseInterface.KEYS.Phone
            yield DatabaseInterface.KEYS.Email
            yield DatabaseInterface.KEYS.Street
            yield DatabaseInterface.KEYS.City
            yield DatabaseInterface.KEYS.State
            yield DatabaseInterface.KEYS.Zip

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
                       (row[DatabaseInterface.KEYS.Street],
                       row[DatabaseInterface.KEYS.City],
                       row[DatabaseInterface.KEYS.State],
                       row[DatabaseInterface.KEYS.Zip]))

    @property
    def CurrentUser(self):
        return self.__currentUser

    @property
    def Contacts(self):
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        return [self.__rowToContact(row) for row in
                self.__dbConnection.execute('select * from {}'.format(self.__currentUser)).fetchall()]

    @property
    def Users(self):
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        return [row['username'] for row in self.__dbConnection.execute('select username from Users').fetchall()]

    def Connect(self):
        '''Connect to the database for the current user'''
        self.__dbConnection = sqlite3.connect(os.path.join(os.getcwd(), 'contacts.db')
                                              if self.__currentUser != 'DEBUG' else ':memory:')  # debug
        self.__dbConnection.row_factory = sqlite3.Row
        self.__dbConnection.execute('''create table if not exists {} ({} text, {} text, {} int, {} text, {} text, {} text, {} text, {} text)'''
                                    .format(self.__currentUser, *DatabaseInterface.KEYS()))
        self.__dbConnection.execute('''create table if not exists Users (username text PRIMARY KEY, password text)''')

    def UserExists(self):
        '''Returns true if the current user of this database interface exists, false otherwise'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        return 0 != len(
            self.__dbConnection.execute('''select * from Users where username=?''', (self.__currentUser,)).fetchall())

    def RegisterCurrentUser(self, password):
        '''Register a new user to the users table. Raises a UserAlreadyExists exception if username already exists'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        if 0 != len(self.__dbConnection.execute('''select * from Users where username=?''',
                                                (self.__currentUser,)).fetchall()):
            raise UserAlreadyExistsException()
        self.__dbConnection.execute('''insert into Users (username, password) values (?, ?)''',
                                    (self.__currentUser, password))

    def CheckPassword(self, password):
        '''Returns true if the current user exists and his password is password'''
        if self.__dbConnection == None:
            raise DatabaseNotConnectedException()
        if not self.UserExists():
            return False
        try:
            return self.__dbConnection.execute('''select * from Users where username=? and password=?''',
                                               (self.__currentUser, password)).fetchall()[0]['password'] == password
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
            self.__dbConnection.execute('''insert into {} ({}, {}, {}, {}, {}, {}, {}, {}) values (?, ?, ?, ?, ?, ?, ?, ?)'''
                                        .format(self.__currentUser, *DatabaseInterface.KEYS()),
                                        (name[0],
                                         name[1],
                                         contact.phone,
                                         contact.email,
                                         contact.home[0],
                                         contact.home[1],
                                         contact.home[2],
                                         contact.home[3]))

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
                {} like ? or
                {} like ? or
                {} like ? or
                {} like ?'''
                                                       .format(self.__currentUser,
                                                               *DatabaseInterface.KEYS()),
                                                       [searchStr for i in range(8)]).fetchall()]

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
        self.__dbConnection.execute('delete from {} where {}=? and {}=?'
                                    .format(self.__currentUser,
                                            *DatabaseInterface.KEYS()),
                                    (name[0],
                                     name[1]))

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

        self.__dbConnection.execute('update {} set {}=?, {}=?, {}=?, {}=?, {}=?, {}=?, {}=?, {}=? where {}=? and {}=?'
                                    .format(self.__currentUser,
                                            *DatabaseInterface.KEYS(),
                                            *DatabaseInterface.KEYS()),
                                    (newName[0],
                                     newName[1],
                                     newContact.phone,
                                     newContact.email,
                                     newContact.home[0],
                                     newContact.home[1],
                                     newContact.home[2],
                                     newContact.home[3],
                                     name[0],
                                     name[1]))


##########################################UI Code##################################################################

##### Code for Login Page #####
class LoginP():
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.insideFrame = Frame(width=200, height=100)
        master.geometry("950x550+500+150")
        master.resizable(width=True, height=True)
        self.initialItems()

        self.insideFrame.place(x=325, y=325)

        # login button calls check_login when clicked to check inputs
        self.loginButton = Button(self.insideFrame, text='Login', width=28,
                                  command=self.CheckLogin)
        self.loginButton.pack()

        # new user button calls load_registration_window to move to the registration page
        self.newUserButton = Button(self.insideFrame, text='New User Registration', width=28,
                                    command=self.LoadRegistrationPage)
        self.newUserButton.pack()

    # initialItems() contains all entry boxes and labels found on login page
    def initialItems(self):
        self.LoginIDEntry = Entry(self.master, width=25)
        self.LoginIDEntry.place(x=325, y=155)
        self.LoginIDLabel = Label(text="Login ID")
        self.LoginIDLabel.place(x=325, y=175)

        self.LoginPasswordEntry = Entry(show="\u2022", width=25)
        self.LoginPasswordEntry.place(x=325, y=255)
        self.LoginPasswordLabel = Label(text="Password")
        self.LoginPasswordLabel.place(x=325, y=275)

        self.loginFailLabel = Label()
        self.loginFailLabel.place(x=325, y=133)

    def login_input(self):
        return "{}".format(self.LoginIDEntry.get())

    def password_input(self):
        return "{}".format(self.LoginPasswordEntry.get())

    # checks login information by checking if user exists and if so, it checks the username and password
    def CheckLogin(self):
        try:
            with DatabaseInterface(self.login_input()) as db:
                if not db.UserExists():
                   self.loginFailLabel.config(text="User not found", fg="red")
                else:
                   if not db.CheckPassword(self.password_input()):
                       self.loginFailLabel.config(text="Incorrect password", fg="red")
                   else:
                       # move to main page if inputs for username and password are correct
                       self.LoadMainPage(self.login_input())
        except DatabaseNotConnectedException:
            self.loginFailLabel.config(text="Failed to connect to database", fg="red")
        finally:
            db.CloseOut()

    # moves to registration page
    def LoadRegistrationPage(self):
        self.Close()
        self.newWindow = self.master
        self.app = RegisterP(self.newWindow)

    # moves to main page by keeping the user
    def LoadMainPage(self, user):
        self.newWindow = self.master
        self.app = MainP(self.newWindow, user)
        self.Close()

    # destroys every entry box and label on page
    def Close(self):
        self.LoginIDEntry.destroy()
        self.LoginIDLabel.destroy()
        self.LoginPasswordEntry.destroy()
        self.LoginPasswordLabel.destroy()
        self.loginButton.destroy()
        self.newUserButton.destroy()
        if self.loginFailLabel.winfo_exists():
            self.loginFailLabel.destroy()

##### Code for Main Page #####
class MainP():
    def __init__(self, master, user):
        self.master = master
        self.initialItems()
        self.frame = Frame(self.master)
        self.insideFrame = Frame(width=200, height=100)
        self.LogoutFrame = Frame(width=1, height=1)
        master.geometry("950x550+500+150")
        master.resizable(width=True, height=True)

        self.AddressL = Listbox()
        self.AddressL.place(x=0, y=0)
        self.AddressL.config(width=25, height=34)
        self.AddressL.bind("<Double-Button-1>", self.OnDoubleClick)

        self.insideFrame.place(x=275, y=485)

        # connect to the user's phone book
        self.user = DatabaseInterface(user)
        self.user.Connect()
        self.contact = None
        self.operation = None
        self.UpdatePhoneBook()

        # new button calls NewButtonClick to add a contact
        self.newButton = Button(self.insideFrame, text='New', width=18,
                                command=self.NewButtonClick)
        self.newButton.pack(side=LEFT)

        # edit button calls EditButtonClick to edit a contact
        self.editButton = Button(self.insideFrame, text='Edit', width=18,
                                 command=self.EditButtonClick)
        self.editButton.pack(side=LEFT)

        # save button calls SaveButtonClick to save changes
        self.saveButton = Button(self.insideFrame, text='Save', width=18,
                                 command=self.SaveButtonClick)
        self.saveButton.pack(side=LEFT)

        # delete button calls DeleteButtonClick to delete a contact
        self.deleteButton = Button(self.insideFrame, text='Delete', width=18,
                                   command=self.DeleteButtonClick)
        self.deleteButton.pack(side=LEFT)

        # cancel button calls CancelButtonClick to clear all entries
        self.cancelButton = Button(self.insideFrame, text='Cancel', width=18,
                                   command=self.CancelButtonClick)
        self.cancelButton.pack(side=LEFT)

        # logout button calls LogoutButtonClick to log out of database and return to login page
        self.LogoutFrame.place(x=153, y=485)
        self.logoutButton = Button(self.LogoutFrame, text='Log Out', width=18,
                                   command=self.LogoutButtonClick)
        self.logoutButton.pack()

    # initializes all entry boxes and labels, every entry box is set to DISABLED
    def initialItems(self):
        #label to show errors
        self.failLabel = Label()
        self.failLabel.place(x=325, y=133)
        # used for search entry box
        self.searchStr = StringVar()
        self.searchStr.trace("w", self.Search)
        self.searchEntry = Entry(width=35, textvariable=self.searchStr)
        self.searchEntry.place(x=380, y=10)
        self.searchLabel = Label(text="Search")
        self.searchLabel.place(x=325, y=10)

        self.firstNameEntry = Entry(width=25, state=DISABLED)
        self.firstNameEntry.place(x=325, y=155)
        self.firstNameLabel = Label(text="First Name")
        self.firstNameLabel.place(x=250, y=155)

        self.lastNameEntry = Entry(width=25, state=DISABLED)
        self.lastNameEntry.place(x=575, y=155)
        self.lastNameLabel = Label(text="Last Name")
        self.lastNameLabel.place(x=500, y=155)

        self.phoneEntry = Entry(width=25, state=DISABLED)
        self.phoneEntry.place(x=325, y=195)
        self.phoneLabel = Label(text="Phone Number")
        self.phoneLabel.place(x=225, y=195)

        self.emailEntry = Entry(width=25, state=DISABLED)
        self.emailEntry.place(x=325, y=235)
        self.emailLabel = Label(text="Email")
        self.emailLabel.place(x=250, y=235)

        self.streetEntry = Entry(width=25, state=DISABLED)
        self.streetEntry.place(x=325, y=275)
        self.streetLabel = Label(text="Address")
        self.streetLabel.place(x=250, y=275)

        self.cityEntry = Entry(width=25, state=DISABLED)
        self.cityEntry.place(x=325, y=315)
        self.cityLabel = Label(text="City")
        self.cityLabel.place(x=250, y=315)

        self.stateEntry = Entry(width=25, state=DISABLED)
        self.stateEntry.place(x=325, y=355)
        self.stateLabel = Label(text="State")
        self.stateLabel.place(x=250, y=355)

        self.zipEntry = Entry(width=25, state=DISABLED)
        self.zipEntry.place(x=325, y=395)
        self.zipLabel = Label(text="Zip Code")
        self.zipLabel.place(x=250, y=395)

    # updates list box to show matching results
    def Search(self, *args):
        self.AddressL.delete(0, END)
        contacts = sorted(self.user.Search(self.searchStr.get()))
        for contact in contacts:
            self.AddressL.insert(END, contact.name)

    # double click name in list box to show info in entry boxes
    def OnDoubleClick(self, event):
        widget = event.widget
        selection = widget.curselection()
        value = widget.get(selection[0])
        try:
            for contact in self.user.Contacts:
                if contact.name == value:
                    self.clear_entries()
                    self.enabled_state()

                    names = contact.name.split()
                    self.firstNameEntry.insert(0, names[0])
                    self.lastNameEntry.insert(0, names[1])
                    self.phoneEntry.insert(0, contact.phone)
                    self.emailEntry.insert(0, contact.email)
                    self.streetEntry.insert(0, contact.home[0])
                    self.cityEntry.insert(0, contact.home[1])
                    self.stateEntry.insert(0, contact.home[2])
                    self.zipEntry.insert(0, contact.home[3])
                    self.contact = self.RetrieveContact()
                    self.disabled_state()
        except IndexError:
            pass

    # Updates list in ALPHABETICAL ORDER
    def UpdatePhoneBook(self):
        self.user.Commit()
        self.AddressL.delete(0, END)
        contacts = sorted(self.user.Contacts)
        for contact in contacts:
            self.AddressL.insert(END, contact.name)

    # enables entry boxes if a contact is displayed in entry boxes
    def EditButtonClick(self):
        if self.contact != None:
            self.enabled_state()
            self.operation = 2

    def SaveButtonClick(self):
        try:
            if self.entry_state == 'ENABLED':
                # if the entry is for a new contact...
                if self.operation == 1:
                    self.contact = self.RetrieveContact()
                    self.user.AddContact(self.contact)
                # if its for editing an existing contact...
                if self.operation == 2:
                    newContact = self.RetrieveContact()
                    self.user.EditContact(self.contact, newContact)
                self.contact = None
                self.operation = None
                self.UpdatePhoneBook()
                self.clear_entries()
                self.disabled_state()
        except InvalidContactPhoneException:
            self.failLabel.config(text="Invalid phone number", fg="red")
        except InvalidContactEmailException:
            self.failLabel.config(text="Invalid e-mail", fg="red")
        except InvalidContactAddressException:
            self.failLabel.config(text="Invalid zip code", fg="red")
        except TypeError:
            pass

    def NewButtonClick(self):
        self.clear_entries()
        self.enabled_state()
        self.operation = 1

    def DeleteButtonClick(self):
        self.contact = self.RetrieveContact()
        self.user.DeleteContact(self.contact)
        self.UpdatePhoneBook()
        self.clear_entries()

    def CancelButtonClick(self):
        self.clear_entries()
        self.disabled_state()
        self.clear_error_label()

    # returns to main page
    def LogoutButtonClick(self):
        self.DestroyPage()
        self.newWindow = self.master
        self.app = LoginP(self.newWindow)

    def RetrieveContact(self):
        self.firstName = self.firstNameEntry.get()
        self.lastName = self.lastNameEntry.get()
        self.phone = self.phoneEntry.get()
        self.email = self.emailEntry.get()
        self.street = self.streetEntry.get()
        self.city = self.cityEntry.get()
        self.state = self.stateEntry.get()
        self.zip = self.zipEntry.get()
        return Contact(self.firstName,
                       self.lastName,
                       self.phone,
                       self.email,
                       (self.street, self.city, self.state, self.zip))

    # enable entry boxes
    def enabled_state(self):
        self.entry_state = 'ENABLED'
        self.firstNameEntry.config(state='normal')
        self.lastNameEntry.config(state='normal')
        self.phoneEntry.config(state='normal')
        self.emailEntry.config(state='normal')
        self.streetEntry.config(state='normal')
        self.cityEntry.config(state='normal')
        self.stateEntry.config(state='normal')
        self.zipEntry.config(state='normal')

    # disable entry boxes
    def disabled_state(self):
        self.entry_state = 'DISABLED'
        self.firstNameEntry.config(state='readonly')
        self.lastNameEntry.config(state='readonly')
        self.phoneEntry.config(state='readonly')
        self.emailEntry.config(state='readonly')
        self.streetEntry.config(state='readonly')
        self.cityEntry.config(state='readonly')
        self.stateEntry.config(state='readonly')
        self.zipEntry.config(state='readonly')

    def DestroyPage(self):
        self.AddressL.destroy()
        self.firstNameEntry.destroy()
        self.firstNameLabel.destroy()
        self.lastNameEntry.destroy()
        self.lastNameLabel.destroy()
        self.phoneEntry.destroy()
        self.phoneLabel.destroy()
        self.emailEntry.destroy()
        self.emailLabel.destroy()
        self.streetEntry.destroy()
        self.streetLabel.destroy()
        self.cityEntry.destroy()
        self.cityLabel.destroy()
        self.stateEntry.destroy()
        self.stateLabel.destroy()
        self.zipEntry.destroy()
        self.zipLabel.destroy()
        self.searchEntry.destroy()
        self.searchLabel.destroy()
        self.insideFrame.destroy()
        self.LogoutFrame.destroy()
        self.user.CloseOut()
        self.user = None
        self.clear_error_label()

    def clear_entries(self):
        self.enabled_state()
        self.firstNameEntry.delete(0, END)
        self.lastNameEntry.delete(0, END)
        self.phoneEntry.delete(0, END)
        self.emailEntry.delete(0, END)
        self.streetEntry.delete(0, END)
        self.cityEntry.delete(0, END)
        self.stateEntry.delete(0, END)
        self.zipEntry.delete(0, END)
        self.disabled_state()

    def clear_error_label(self):
        if self.failLabel.winfo_exists():
            self.failLabel.destroy()

#### Code for Register Page ####
class RegisterP():
    def __init__(self, master):
        self.master = master
        self.insideFrame = Frame(width=200, height=100)
        self.frame = Frame(self.master)
        self.initialItems()
        master.geometry("950x550+500+150")
        master.resizable(width=False, height=False)

        self.insideFrame.place(x=325, y=305)
        # register button calls registerUser to register a new user
        self.registerButton = Button(self.insideFrame, text='Register', width=28,
                                     command=self.RegisterUser)
        self.registerButton.pack()

        # cancel button calls cancel_registration to clear entries and return to login page
        self.cancelButton = Button(self.insideFrame, text='Cancel', width=28,
                                   command=self.CancelRegistration)
        self.cancelButton.pack()

    # registers a new user if user does not exist and inputs are acceptable
    def RegisterUser(self):
        try:
            self.usernameInput = self.usernameEntry.get()
            self.passwordInput = self.passwordEntry.get()
            self.reenteredPasswordInput = self.reenterPasswordEntry.get()

            if self.passwordInput == self.reenteredPasswordInput:
                with DatabaseInterface(self.usernameInput) as db:
                    db.Connect()
                    db.RegisterCurrentUser(self.passwordInput)
                    self.LoadMainPage(db.CurrentUser)
                    db.CloseOut
            else:
                self.errorLabel.config(text="Passwords do not match", fg="red")
        except TypeError:
            pass
        except UserAlreadyExistsException:
            self.errorLabel.config(text="User already exists", fg="red")
        except DatabaseNotConnectedException:
            self.errorLabel.config(text="Failed to connect to database", fg="red")

    # initializes all entry boxes and labels
    def initialItems(self):
        self.usernameEntry = Entry(width=25)
        self.usernameEntry.place(x=325, y=155)
        self.userNameLabel = Label(text="Username: ")
        self.userNameLabel.place(x=325, y=175)

        self.passwordEntry = Entry(width=25, show="\u2022")
        self.passwordEntry.place(x=575, y=155)
        self.passwordLabel = Label(text="Password: ")
        self.passwordLabel.place(x=575, y=175)

        self.reenterPasswordEntry = Entry(width=25, show="\u2022")
        self.reenterPasswordEntry.place(x=325, y=195)
        self.reenterPasswordLabel = Label(text="Re-Enter Password: ")
        self.reenterPasswordLabel.place(x=325, y=215)

        self.errorLabel = Label()
        self.errorLabel.place(x=325, y=133)

    def Close(self):
        self.usernameEntry.destroy()
        self.passwordEntry.destroy()
        self.reenterPasswordEntry.destroy()
        self.userNameLabel.destroy()
        self.passwordLabel.destroy()
        self.reenterPasswordLabel.destroy()
        self.registerButton.destroy()
        self.cancelButton.destroy()
        if self.errorLabel.winfo_exists():
            self.errorLabel.destroy()

    # cancels entries and returns to login page
    def CancelRegistration(self):
        self.Close()
        self.newWindow = self.master
        self.app = LoginP(self.newWindow)

    def LoadMainPage(self, user):
        self.newWindow = self.master
        self.app = MainP(self.newWindow, user)
        self.Close()

def main():
    root = Tk()
    root.wm_title('Address Book')
    app = LoginP(root)
    root.mainloop()

if __name__ == '__main__':
    main()