import os

class Contact:
    def __init__(self, first_name, last_name, phone, email, home):
        self.name = first_name + last_name
        self.phone = phone
        self.email = email
        self.home = home
        
    def __str__(self):
        return("Name: {0}\n Phone Number: {1}\n E-mail Address: {2}\n Home Address {3} ").format(self.name, self.phone, self.email, self.home)

    def edit_name(self, first_name, last_name):
        self.name = first_name + last_name

    def edit_email(self, email):
        self.email = email

    def edit_phone(self, phone):
        self.phone = phone

    def edit_home(self, home):
        self.home = home

def retrieveContactInfo():
    try:
        contact_first_name = input("First Name: ")
        contact_last_name = input("Last Name: ")
        contact_phone = input("Phone Number: ")
        contact_email = input("E-mail Address: ")
        return contact
    except SyntaxError:
        print("Missing input")
    #incomplete on exceptions

def addContact():
    contacts_list = []

    try:
        contact = retrieveContactInfo()
        #contacts_list.append(contact)
    #incomplete
    except SyntaxError:
        print("Random Error is used")

def displayContacts():
    for contact in contacts_list:
        print(contact.first_name, contact.last_name)

def searchContact():
    search_contact = input("Contact: ")
    search_contact = search_contact.lower()
    is_found = False

    for contact in contacts_list:
        contact_name = contact.name
        contact_name = contact_name.lower()

        if contact_name == search_contact_name:
            is_found = True
            break

    if not is_found:
        print("No Results Found")
    else:
        showContact(contact_name)

def showContact(contact):
    str(contact)

def deleteContact(contact):
    del contact
