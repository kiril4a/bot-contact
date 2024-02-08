import re
from collections import UserDict
from datetime import datetime
import json

class Field:
    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.validate(new_value)
        self.__value = new_value

    @staticmethod
    def validate(value):
        pass  

class Name(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate()

    def validate(self):
        try:
            datetime.strptime(self.value, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate()

    def validate(self):
        if not re.fullmatch(r"\d{10}", self.value):
            raise ValueError("Phone number must have 10 digits")



class Record:
    def __init__(self, name, phones=None, birthday=None):
        self.name = Name(name)
        self.phones = [Phone(phone) for phone in phones] if phones else []
        self.birthday = Birthday(birthday) if birthday else None

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
                p._Field__value = new_phone  
                p.validate()
                return True
        raise ValueError("The old phone number does not exist.")
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now()
            next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day)
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day)
            days_remaining = (next_birthday - today).days
            return days_remaining
        return None

class AddressBook(UserDict):
    def __init__(self, page_size=5):
        super().__init__()
        self.page_size = page_size

    def __iter__(self):
        return self.paginated_iterator()

    def paginated_iterator(self):
        values = list(self.data.values())
        for i in range(0, len(values), self.page_size):
            yield values[i:i + self.page_size]

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

    def find(self, search_str):
        results = []
        for record in self.data.values():
            if (
                search_str.lower() in record.name.value.lower()
                or any(search_str.lower() in phone.value.lower() for phone in record.phones)
            ):
                results.append(record)
        return results


    def save_to_file(self, filename):
        with open(filename, "w") as file:
            for name, record in self.data.items():
                data = {
                    "name": record.name.value,
                    "phones": [phone.value for phone in record.phones],
                    "birthday": record.birthday.value if record.birthday else None
                }
                file.write(json.dumps(data) + "\n")

    def load_from_file(self, filename):
        with open(filename, "r") as file:
            self.data = {}
            for line in file:
                data = json.loads(line.strip())
                name = data["name"]
                phones = data.get("phones", [])
                birthday = data.get("birthday")
                self.data[name] = Record(name=name, phones=phones, birthday=birthday)

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
        except TypeError as e:
            return str(e)
    return inner



def add_contact(address_book, name, phone):
    if not isinstance(name, str) or not (isinstance(phone, str) and phone.isdigit()):
        raise TypeError("Invalid input types. Name should be a string and phone number should be a number or a string of digits.")
    
    phone = ''.join(filter(str.isdigit, phone))

    if name in address_book:
        address_book[name].add_phone(phone)
        return f"Phone number added to contact {name}."
    else:
        address_book.add_record(Record(name, [phone]))
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
    
def search_contacts(address_book, search_str):
    results = address_book.find(search_str)
    if results:
        return "\n".join([f"{record.name.value}: {', '.join([phone.value for phone in record.phones])}" for record in results])
    else:
        return f"No contacts found for '{search_str}'."


def show_phone(address_book, name):
    if name not in address_book:
        raise KeyError
    record = address_book[name]
    phone_numbers = ", ".join([phone.value for phone in record.phones])
    return f"{name}: {phone_numbers}"

def show_all(address_book):
    return "\n".join([f"{record.name.value}: {', '.join([phone.value for phone in record.phones])}" 
                      for records in address_book for record in records])



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
    elif cmd == "show" and len(parts) == 2 and parts[1] == "all":
        return show_all(contacts)
    elif cmd in ["add", "change"] and len(parts) != 3:
        raise ValueError("Invalid input. Please enter command, name, and phone number.")
    elif cmd == "add":
        return add_contact(contacts, parts[1], parts[2])
    elif cmd == "change":
        return change_phone(contacts, parts[1], parts[2])
    elif cmd == "phone":
        return show_phone(contacts, parts[1])
    elif cmd == "find":
        return search_contacts(contacts, ' '.join(parts[1:]))
    elif cmd == "delete" and len(parts) == 2:
        return delete_contact(contacts, parts[1])
    elif cmd == "show" and len(parts) == 2 and parts[1] == "all":
        return show_all(contacts)
    else:
        raise ValueError("Invalid command")


def main():
    address_book = AddressBook()
    try:
        address_book.load_from_file("address_book.txt")
    except FileNotFoundError:
        print("No existing data file found. Starting with an empty address book.")

    while True:
        command = input("Enter your command: ")
        if command.lower() in ["good bye", "close", "exit"]:
            address_book.save_to_file("address_book.txt")
            print("Good bye!")
            break
        try:
            response = handle_command(command, address_book)
            print(response)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()