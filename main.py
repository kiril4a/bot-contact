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

def add_contact(contacts, name, phone):
    if not isinstance(name, str) or not (isinstance(phone, str) and phone.isdigit()):
        raise TypeError
    if name in contacts:
        return f"Contact {name} already exists. Use 'change' to modify the phone number."
    contacts[name] = phone
    return f"Contact {name} added successfully."

def change_phone(contacts, name, phone):
    if not isinstance(name, str) or not (isinstance(phone, str) and phone.isdigit()):
        raise TypeError
    if name not in contacts:
        raise KeyError
    contacts[name] = phone
    return f"Phone number for {name} changed successfully."

def show_phone(contacts, name):
    if name not in contacts:
        raise KeyError
    return f"{name}: {contacts[name]}"

def show_all(contacts):
    return "\n".join([f"{name}: {phone}" for name, phone in contacts.items()])

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
    elif cmd == "show" and len(parts) == 2 and parts[1] == "all":
        return show_all(contacts)
    else:
        raise ValueError("Invalid command")

def main():
    contacts = {}
    while True:
        command = input("Enter your command: ")
        if command.lower() in ["good bye", "close", "exit"]:
            print("Good bye!")
            break
        try:
            response = handle_command(command, contacts)
            print(response)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
