import re
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self._value = value  # Приватне поле для зберігання значення

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

class Name(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate()

    def validate(self):
        try:
            datetime.strptime(self._value, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

    # Додавання setter для полегшення встановлення значення
    @Field.value.setter
    def value(self, new_value):
        self._value = new_value
        self.validate()

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate()

    def validate(self):
        if not re.fullmatch(r"\d{10}", self._value):
            raise ValueError("Phone number must have 10 digits")

    # Додавання setter для полегшення встановлення значення
    @Field.value.setter
    def value(self, new_value):
        self._value = new_value
        self.validate()

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

    def edit_phone(self, new_phone, new_birthday=None):
        if not self.phones:
            raise ValueError("No existing phone number for this contact.")
        
        self.phones[0].value = Phone(new_phone).value

        if new_birthday:
            self.birthday = Birthday(new_birthday)

        return True

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
    def __init__(self):
        super().__init__()
        self.page_size = 5

    def iterator(self):
        for i in range(0, len(self.data), self.page_size):
            yield list(self.data.values())[i:i+self.page_size]

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

def add_contact(address_book, name, phone, birthday=None):
    if not isinstance(name, str) or not (isinstance(phone, str) and phone.isdigit()):
        raise TypeError("Invalid input types. Name should be a string and phone number should be a number or a string of digits.")

    if birthday and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", birthday):
        raise TypeError("Invalid birthday format. Please use YYYY-MM-DD.")
    
    if name in address_book.data:
        address_book.data[name].add_phone(phone)
        if birthday:
            address_book.data[name].birthday = Birthday(birthday)
        return f"Phone number added to contact {name}."
    else:
        record = Record(name, [phone], birthday)
        address_book.add_record(record)
        return f"Contact {name} added successfully."

def change_phone(address_book, name, new_phone, new_birthday=None):
    if not isinstance(name, str) or not (isinstance(new_phone, str) and new_phone.isdigit()):
        raise TypeError("Invalid input types. Name should be a string, and the new phone number should be a number or a string of digits.")

    if name not in address_book.data:
        raise KeyError("No such contact found.")

    record = address_book.data[name]

    if record.phones:
        record.edit_phone(new_phone, new_birthday)
        return f"Phone number for {name} changed successfully."
    else:
        raise ValueError(f"No existing phone number for {name}.")

def show_phone(address_book, name):
    if name not in address_book.data:
        raise KeyError("No such contact found.")

    record = address_book.data[name]

    phone_numbers = ", ".join([phone.value for phone in record.phones])
    birthday_info = f" | Birthday: {record.birthday.value}" if record.birthday else ""
    
    return f"{name}: {phone_numbers}{birthday_info}"


def show_all(address_book, page=1):
    page -= 1
    records = list(address_book.iterator())
    if page < len(records):
        return "\n".join([f"{record.name.value}: {', '.join([phone.value for phone in record.phones])} | Birthday: {record.birthday.value if record.birthday else 'N/A'}"
                          for record in records[page]])
    else:
        return "Page not found."


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
    
    elif cmd == "add":
        if len(parts) == 3:
            try:
                return add_contact(contacts, parts[1], parts[2])
            except TypeError:
                return "Invalid input types. Name should be a string and phone number should be a number or a string of digits."
        elif len(parts) == 4:
            try:
                return add_contact(contacts, parts[1], parts[2], parts[3])
            except TypeError:
                return "Invalid input types. Name should be a string, phone number should be a number or a string of digits, and birthday should be in the format YYYY-MM-DD."
        else:
            return "Invalid input. Please enter command, name, phone number, and optional birthday in the format YYYY-MM-DD."
    elif cmd == "change" and len(parts) in [3, 4]:
        try:
            if len(parts) == 4:
                return change_phone(contacts, parts[1], parts[2], parts[3])
            else:
                return change_phone(contacts, parts[1], parts[2])
        except ValueError as e:
            return str(e)
    elif cmd == "phone":
        return show_phone(contacts, parts[1])
    elif cmd == "find":
        return show_phone(contacts, parts[1])
    elif cmd == "delete" and len(parts) == 2:
        return delete_contact(contacts, parts[1])
    elif cmd == "show" and len(parts) == 3 and parts[1] == "all":
        try:
            page = int(parts[2])
            return show_all(contacts, page)
        except ValueError:
            return "Invalid page number. Please enter an integer."
    elif cmd == "show" and len(parts) == 2:
        return "Please enter page number."
    else: 
        return "Unknown command."

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
