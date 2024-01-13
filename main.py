def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "No such contact found."
        except ValueError:
            return "Invalid input. Please enter a name and phone number."
        except IndexError:
            return "Enter user name and phone number."
    return inner

def add_contact(contacts, name, phone):
    contacts[name] = phone
    return f"Contact {name} added successfully."

def change_phone(contacts, name, phone):
    if name in contacts:
        contacts[name] = phone
        return f"Phone number for {name} changed successfully."
    else:
        raise KeyError

def show_phone(contacts, name):
    return contacts[name]

def show_all(contacts):
    return "\n".join([f"{name}: {phone}" for name, phone in contacts.items()])

@input_error
def handle_command(command, contacts=None):
    parts = command.split()
    cmd = parts[0].lower()
    if cmd == "hello":
        return "How can I help you?"
    elif cmd == "add":
        return add_contact(contacts, parts[1], parts[2])
    elif cmd == "change":
        return change_phone(contacts, parts[1], parts[2])
    elif cmd == "phone":
        return show_phone(contacts, parts[1])
    elif cmd == "show" and parts[1] == "all":
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
        response = handle_command(command, contacts)
        print(response)

if __name__ == "__main__":
    main()
