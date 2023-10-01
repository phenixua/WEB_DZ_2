import json
import re
from datetime import datetime
from prettytable import PrettyTable
from collections import UserDict
from colorama import Fore, Style
from abc import ABC, abstractmethod


# Абстрактний клас DataPrinter з абстрактним методом show_all()
class DataPrinter(ABC):
    @abstractmethod
    def show_all(self, data):
        pass


# Конкретна реалізація DataPrinter для виводу в консоль
class ConsoleDataPrinter(DataPrinter):
    def show_all(self, data):
        for item in data:
            print(item)
            print('-' * 30)


# Спочатку визначимо інтерфейс UserView
class UserView:
    def show(self, message):
        pass


# Створимо конкретну реалізацію UserView для виведення інформації у консоль
class ConsoleUserView(UserView):
    def show(self, message):
        print(message)


# Далі визначимо інтерфейс для об'єкта, який зберігатиме дані (DataStorage)
class DataStorage:
    def add(self, key, value):
        pass

    def get(self, key):
        pass

    def delete(self, key):
        pass


# Реалізація DataStorage
class InMemoryDataStorage(DataStorage):
    def __init__(self):
        self.data = {}

    def add(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        if key in self.data:
            del self.data[key]


# Тепер визначимо клас Field, який буде використовуватися для полів контактів
class Field:
    def __init__(self, value):
        self.value = value


# Реалізація Phone
class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Invalid phone number")
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        # Перевірка формату +38-000-0000000 або +380000000000
        if re.match(r'^\+\d{2}-\d{3}-\d{7}$', value) or re.match(r'^\+\d{12}$', value):
            return True
        # Перевірка формату 000-0000000 або 0000000000
        if re.match(r'^\d{3}-\d{7}$', value) or re.match(r'^\d{10}$', value):
            return True
        return False

    def __str__(self):
        return self.value


# Реалізація Email
class Email(Field):
    def __init__(self, value):
        if not self.validate_email(value):
            raise ValueError("Invalid email")
        super().__init__(value)

    @staticmethod
    def validate_email(value):
        email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+(\.\w+)+$')
        return bool(email_pattern.match(value))

    def __str__(self):
        return self.value


# Реалізація Name
class Name(Field):
    def __str__(self):
        return self.value


# Реалізація Address
class Address(Field):
    def __str__(self):
        return self.value


# Реалізація Birthday
class Birthday(Field):
    def __init__(self, value):
        if not self.validate_birthday(value):
            raise ValueError("Invalid birthday")
        super().__init__(value)

    @staticmethod
    def validate_birthday(value):
        return isinstance(value, datetime) and value <= datetime.now()

    def __str__(self):
        return self.value.strftime('%Y-%m-%d')


# Реалізація класу Record для зберігання контактної інформації
class Record:
    def __init__(self, name: Name, address: Address, phones: list, emails: list = None, birthday: Birthday = None):
        self.name = str(name)
        self.address = str(address)
        self.phones = self.process_phones(phones)
        self.emails = [str(email) for email in emails] if emails else []
        self.birthday = birthday

    def process_phones(self, phones):
        processed_phones = []
        for phone_field in phones:
            phone = str(phone_field)
            phone_numbers = re.split(r'[,\s]+', phone)
            for phone_number in phone_numbers:
                if Phone.validate_phone(phone_number):
                    processed_phones.append(str(Phone(phone_number)))
                else:
                    raise ValueError(f"Error: Invalid phone number: {phone_number}")
        return processed_phones

    def add_phone(self, phone):
        try:
            phone_number = Phone(phone)
            self.phones.append(phone_number)
            self.update_record_phones()
            return f"Phone number {phone} added for {self.name}"
        except ValueError as e:
            return f"Error: {e}"

    def delete_phone(self, phone):
        new_phones = [p for p in self.phones if p.value != phone]
        self.phones = new_phones

    def edit_phone(self, old_phone, new_phone):
        old_phone_found = False
        for i, phone in enumerate(self.phones):
            if phone == old_phone:
                old_phone_found = True
                try:
                    self.phones[i] = new_phone
                    return f"Phone number updated for {self.name}\nOld phone number: {old_phone}\nNew phone number: {new_phone}"
                except ValueError as e:
                    return f"Error: {e}\nPlease enter a valid phone number."

        if not old_phone_found:
            return f"Error: Old phone number {old_phone} not found in {self.name}'s record."

    def update_record_phones(self):
        self.phones = [str(phone) for phone in self.phones]

    def days_to_birthday(self):
        if not self.birthday:
            return None

        today = datetime.now().date()
        next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day).date()

        if today > next_birthday:
            next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day).date()

        days_left = (next_birthday - today).days
        return days_left

    def __str__(self):
        result = f"Name: {self.name}\n"
        result += f"Address: {self.address}\n"
        result += f"Phones: {', '.join(self.phones)}\n"
        result += f"Emails: {', '.join(self.emails)}\n"
        if self.birthday:
            result += f"Birthday: {self.birthday}\n"
        result += "-" * 30
        return result


# Визначимо інтерфейс для роботи з адресною книгою
class AddressBookInterface:
    def add_record(self, record: Record):
        pass

    def iterator(self):
        pass

    def save_to_file(self, filename):
        pass

    @classmethod
    def load_from_file(cls, filename):
        pass

    def search_records(self, query):
        pass

    def get_upcoming_birthday_contacts(self, days):
        pass


# Реалізація AddressBook
class AddressBook(AddressBookInterface, UserDict):
    def add_record(self, record: Record):
        self.data[record.name] = record

    def iterator(self):
        return self.data.values()

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            data = {
                "records": [record.__dict__ for record in self.values()]
            }
            for record_data in data["records"]:
                if record_data["birthday"]:
                    record_data["birthday"] = record_data["birthday"].value.strftime('%Y-%m-%d')
            json.dump(data, file, indent=4)

    @classmethod
    def load_from_file(cls, filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                book = cls()
                for record_data in data["records"]:
                    name = Name(record_data["name"])
                    address = Address(record_data["address"])
                    phones = [Phone(phone) for phone in record_data["phones"]]
                    emails = [Email(email) for email in record_data["emails"]]
                    birthday = Birthday(datetime.strptime(record_data["birthday"], "%Y-%m-%d")) if record_data[
                        "birthday"] else None
                    record = Record(name, address, phones, emails, birthday)
                    book.add_record(record)
                return book
        except FileNotFoundError:
            return cls()

    def search_records(self, query):
        query = query.lower()
        found_records = []
        found_record_names = set()

        for record in self.data.values():
            if query in record.name.lower() and record.name not in found_record_names:
                found_records.append(record)
                found_record_names.add(record.name)

            for phone in record.phones:
                if query in phone.lower() and record.name not in found_record_names:
                    found_records.append(record)
                    found_record_names.add(record.name)

            for email in record.emails:
                if query in email.lower():
                    found_records.append(record)
                    break

        return found_records

    def get_upcoming_birthday_contacts(self, days):
        today = datetime.now().date()
        upcoming_birthday_contacts = []

        for record in self.data.values():
            if record.birthday:
                if isinstance(record.birthday, str):
                    record.birthday = Birthday(datetime.strptime(record.birthday, "%Y-%m-%d"))

                next_birthday = datetime(today.year, record.birthday.value.month, record.birthday.value.day).date()
                if today > next_birthday:
                    next_birthday = datetime(today.year + 1, record.birthday.value.month,
                                             record.birthday.value.day).date()
                days_left = (next_birthday - today).days

                if days_left == days:
                    upcoming_birthday_contacts.append(record)

        return upcoming_birthday_contacts


# Основна функція для роботи з програмою
def main():
    data_storage = InMemoryDataStorage()
    user_view = ConsoleUserView()
    book = AddressBook()
    data_printer = ConsoleDataPrinter()  # Створення об'єкта для виводу даних

    while True:
        menu = PrettyTable()
        menu.field_names = [Fore.BLUE + "Option", Fore.BLUE + "Description"]

        menu.add_row(["1", "Add a Contact"])
        menu.add_row(["2", "Edit a Contact"])
        menu.add_row(["3", "Delete a Contact"])
        menu.add_row(["4", "List All Contacts"])
        menu.add_row(["5", "Save Address Book"])
        menu.add_row(["6", "Load Address Book"])
        menu.add_row(["7", "Search Contacts"])
        menu.add_row(["8", "View Upcoming Birthdays"])
        menu.add_row(["9", "Exit"])

        user_view.show(Fore.BLUE + "Address Book Menu:")
        user_view.show(menu)

        choice = input(Fore.YELLOW + "Enter your choice (1/2/3/4/5/6/7/8/9): " + Style.RESET_ALL)

        if choice == "1":
            while True:
                user_view.show("Enter contact details (or enter '0' to exit):")
                name = input("Enter the contact's name: ")
                if name == '0':
                    break

                address = input("Enter the contact's address: ")
                if address == '0':
                    break

                phone = input("Enter the contact's phone number: ")
                if phone == '0':
                    break

                email = input("Enter the contact's email address: ")
                if email == '0':
                    break

                birthday = input("Enter the contact's birthday (YYYY-MM-DD): ")
                if birthday == '0':
                    break

                if name and address and phone and email and birthday:
                    try:
                        name_field = Name(name)
                        address_field = Address(address)
                        phone_field = Phone(phone)
                        email_field = Email(email)
                        birthday_field = Birthday(datetime.strptime(birthday, "%Y-%m-%d"))
                        record = Record(name_field, address_field, [phone_field], [email_field], birthday_field)
                        book.add_record(record)
                        user_view.show(f"Contact {name} added successfully!")
                    except ValueError as e:
                        user_view.show(f"Error: {e}")
                        user_view.show("Please enter valid data.")
                else:
                    user_view.show("All fields are required. Please try again or enter '0' to cancel.")

        elif choice == "2":
            name = input("Enter the contact's name to edit: ")
            if name in book.data:
                record = book.data[name]
                user_view.show(f"Editing Contact: {record.name}")
                user_view.show("1. Edit Name")
                user_view.show("2. Edit Address")
                user_view.show("3. Edit Phone")
                user_view.show("4. Edit Email")
                user_view.show("5. Edit Birthday")
                edit_choice = input("Enter your choice (1/2/3/4/5): ")

                if edit_choice == "1":
                    while True:
                        new_name = input("Enter the new name: ")
                        try:
                            record.name = new_name
                            user_view.show(f"Contact {name} name updated to {new_name}")
                            break
                        except ValueError as e:
                            user_view.show(f"Error: {e}")
                            user_view.show("Please enter a valid name.")

                elif edit_choice == "2":
                    while True:
                        new_address = input("Enter the new address: ")
                        try:
                            record.address = new_address
                            user_view.show(f"Address updated for {record.name}")
                            break
                        except ValueError as e:
                            user_view.show(f"Error: {e}")
                            user_view.show("Please enter a valid address.")

                elif edit_choice == "3":
                    action = input("Enter '1' to edit an existing phone number or '2' to add a new one: ")
                    if action == "1":
                        old_phone = input("Enter the old phone number: ")
                        new_phone = input("Enter the new phone number: ")
                        try:
                            result = record.edit_phone(old_phone, new_phone)
                            user_view.show(result)
                        except ValueError as e:
                            user_view.show(f"Error: {e}")
                            user_view.show("Please enter a valid phone number.")
                    elif action == "2":
                        new_phone = input("Enter the new phone number: ")
                        result = record.add_phone(new_phone)
                        user_view.show(result)

                elif edit_choice == "4":
                    while True:
                        new_email = input("Enter the new email address: ")
                        try:
                            record.emails[0] = new_email
                            user_view.show(f"Email address updated for {record.name}")
                            break
                        except ValueError as e:
                            user_view.show(f"Error: {e}")
                            user_view.show("Please enter a valid email address.")

                elif edit_choice == "5":
                    while True:
                        new_birthday = input("Enter the new birthday (YYYY-MM-DD): ")
                        try:
                            record.birthday = Birthday(datetime.strptime(new_birthday, "%Y-%m-%d"))
                            user_view.show(f"Birthday updated for {record.name}")
                            break
                        except ValueError as e:
                            user_view.show(f"Error: {e}")
                            user_view.show("Please enter a valid birthday (YYYY-MM-DD).")

        elif choice == "3":
            name = input("Enter the contact's name to delete: ")
            if name in book.data:
                del book.data[name]
                user_view.show(f"Contact {name} deleted successfully!")

        elif choice == "4":
            user_view.show("List of All Contacts:")
            data_printer.show_all(book.data.values())  # Виклик методу для виводу даних

        elif choice == "5":
            filename = input("Enter the filename to save the address book (address_book.json): ")
            book.save_to_file(filename)
            user_view.show(f"Address book saved to {filename} successfully!")

        elif choice == "6":
            filename = input("Enter the filename to load the address book from (address_book.json): ")
            book = AddressBook.load_from_file(filename)
            user_view.show(f"Address book loaded from {filename} successfully!")

        elif choice == "7":
            query = input("Enter a search query: ")
            found_records = book.search_records(query)
            if found_records:
                user_view.show("Search Results:")
                data_printer.show_all(found_records)  # Виклик методу для виводу даних
            else:
                user_view.show("No matching records found.")

        elif choice == "8":
            days = int(input("Enter the number of days for upcoming birthdays: "))
            upcoming_birthday_contacts = book.get_upcoming_birthday_contacts(days)
            if upcoming_birthday_contacts:
                user_view.show(f"Upcoming Birthdays in {days} days:")
                data_printer.show_all(upcoming_birthday_contacts)  # Виклик методу для виводу даних
            else:
                user_view.show("No upcoming birthdays found.")

        elif choice == "9":
            user_view.show("Exiting the Address Book program. Goodbye!")
            break

        else:
            user_view.show("Invalid choice. Please enter a valid choice (1/2/3/4/5/6/7/8/9)")


if __name__ == "__main__":
    main()
