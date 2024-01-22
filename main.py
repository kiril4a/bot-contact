import re
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate()

    def validate(self):
        if not re.fullmatch(r"\d{10}", self.value):
            raise ValueError("Phone number must have 10 digits")

class Record:
    def __init__(self, name, phones=None):
        self.name = Name(name)
        self.phones = [Phone(phone) for phone in phones] if phones else []

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        return False

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return True
        raise ValueError("The old phone number does not exist.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

class AddressBook(UserDict):
    def add_record(self, record):
        if isinstance(record, Record):
            self.data[record.name.value] = record
        else:
            raise ValueError("Invalid record type")
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def find(self, name):
        return self.data.get(name)

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "No such contact found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter user name and phone number."
        except TypeError:
            return "Invalid input types. Name should be a string and phone number should be a number or a string of digits."
    return inner

def add_contact(address_book, name, phone):
    if not isinstance(name, str) or not (isinstance(phone, str) and phone.isdigit()):
        raise TypeError
    if name in address_book:
        address_book[name].add_phone(phone)
        return f"Phone number added to contact {name}."
    else:
        record = Record(name, [phone])
        address_book.add_record(record)
        return f"Contact {name} added successfully."

def change_phone(address_book, name, phone):
    if not isinstance(name, str) or not (isinstance(phone, str) and phone.isdigit()):
        raise TypeError
    if name not in address_book:
        raise KeyError
    record = address_book[name]
    if record.phones:
        old_phone = record.phones[0].value
        record.edit_phone(old_phone, phone)
        return f"Phone number for {name} changed successfully."
    else:
        raise ValueError(f"No existing phone number for {name}.")

def show_phone(address_book, name):
    if name not in address_book:
        raise KeyError
    record = address_book[name]
    phone_numbers = ", ".join([phone.value for phone in record.phones])
    return f"{name}: {phone_numbers}"

def show_all(address_book):
    return "\n".join([f"{name}: {', '.join([phone.value for phone in record.phones])}" 
                      for name, record in address_book.items()])


def delete_contact(address_book, name):
    if not isinstance(name, str):
        raise TypeError
    if name not in address_book:
        raise KeyError
    address_book.delete(name)
    return f"Contact {name} deleted successfully."

@input_error
def handle_command(command, contacts=None):
    parts = command.split()
    if not parts:
        raise ValueError("No command entered.")
    cmd = parts[0].lower()

    if cmd == "hello":
        return "How can I help you?"
    elif cmd in ["add", "change"] and len(parts) != 3:
        raise ValueError("Invalid input. Please enter command, name and phone number.")
    elif cmd == "add":
        return add_contact(contacts, parts[1], parts[2])
    elif cmd == "change":
        return change_phone(contacts, parts[1], parts[2])
    elif cmd == "phone":
        return show_phone(contacts, parts[1])
    elif cmd == "find":
        return show_phone(contacts, parts[1])
    elif cmd == "delete" and len(parts) == 2:
        return delete_contact(contacts, parts[1])
    elif cmd == "show" and len(parts) == 2 and parts[1] == "all":
        return show_all(contacts)
    else:
        raise ValueError("Invalid command")

def main():
    address_book = AddressBook()
    while True:
        command = input("Enter your command: ")
        if command.lower() in ["good bye", "close", "exit"]:
            print("Good bye!")
            break
        try:
            response = handle_command(command, address_book)
            print(response)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
