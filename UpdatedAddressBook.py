# python ./AddressBook.py

import os

class Contact:
    
    def __init__(self, first_name = "", last_name = "", phone = "" , email = "", street_address = "", home_city = "", home_state = "", home_zip = ""):
        self.name = first_name + " " +  last_name

        assert len(str(phone)) == 10 or len(str(phone)) == 11, "phone number must be 10 numbers (including area code)"
        self.phone = phone

        assert '@' in email, "e-mail must contain a domain"
        self.email = email

        assert len(str(home_zip)) == 5, "zip code must be 5 numbers"
        self.home = street_address + "\n" + home_city + ", " + home_state + " " + str(home_zip)

    def __str__(self):
        return("Name: {0}\nPhone Number: {1}\nE-mail Address: {2}\nHome Address: {3} ").format(self.name, self.phone, self.email, self.home)

    def name(self, first_name, last_name):
        self.name = first_name + " " + last_name

    def email(self, email):
        assert '@' in email, "e-mail must contain a domain"
        self.email = email

    def phone(self, phone):
        assert len(str(phone)) == 10 or len(str(phone)) == 11, "phone number must be 10 numbers (including area code)"
        self.phone = phone

    def home(self, street_address = "", home_city = "", home_state = "", home_zip = ""):
        assert len(str(home_zip)) == 5, "zip code must be 5 numbers"
        self.home = street_address + " " + home_city + ", " + home_state + " " + home_zip

contacts_list = []

def retrieveContactInfo():
    try:
        contact_first_name = str(input("First Name: "))
        contact_last_name = str(input("Last Name: "))
        contact_phone = int(input("Phone Number: "))
        contact_email = str(input("E-mail Address: "))
        contact_street = str(input("Enter street address: "))
        contact_city = str(input("Enter city: "))
        contact_state = str(input("Enter state: "))
        contact_zip = int(input("Enter zip code: "))

        contact = Contact(contact_first_name, contact_last_name, contact_phone, contact_email,contact_street, contact_city, contact_state, contact_zip)
        return contact
    except ValueError:
        print("Not a valid entry")

def addContact():
    try:
        contact = retrieveContactInfo()
        contacts_list.append(contact)
    #incomplete
    except ValueError:
        print("Error in the entry")


def displayContacts():
    if len(contacts_list) == 0:
        for contact in contacts_list:
            print(contact.name)
    else:
        "No Contacts"

def searchContact():
    found_contacts_list = []
    search_contact = input("Search by Name or Number: ")
    search_contact_input = search_contact.lower()

    for contact in contacts_list:
        contact_name = contact.name
        contact_name = contact_name.lower()

        if search_contact_input in contact_name or contact.phone == search_contact_input:
            found_contacts_list.append(contact)

    if found_contacts_list == []:
        print("No Results Found")
    else:
        showContactInfo(contact)

def showContactInfo(contact):
    #incomplete until GUI
    # Just return values into corresponding fields
    print(contact)
    #str(contact)

def deleteContact():
    try:
        if contacts_list == []:
            print("No Contacts")
        else:
            nameToDelete = input("Enter the name to delete:" )

            for i in range(0, len(contacts_list)):
                currContact = contacts_list[i].name
                if nameToDelete in currContact:
                    print("deleting {0} ...".format(currContact))
                    del contacts_list[i]
    except IndexError:
        print("Out of range")

if __name__ == "__main__":
    
    addContact()
    displayContacts()
    searchContact()
    deleteContact()
    displayContacts()