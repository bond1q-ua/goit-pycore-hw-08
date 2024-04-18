from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name=None):
        if name is None:
            raise ValueError
        super().__init__(name)


class Phone(Field):
    def __init__(self, phone):
        if len(phone) != 10:
            raise ValueError("Wrong number format!")
        super().__init__(phone)


class Birthday(Field):
    def __init__(self, birthday):
        try:
            super().__init__(birthday)
            self.birthday = datetime.strptime(birthday, "%d.%m.%Y").date()

        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = list()
        self.birthday = None

    def add_phone(self, phone):
        if self.find_phone(phone):
            return
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone = self.find_phone(phone)
        if phone:
            self.phones.remove(phone)
            return
        raise ValueError

    def edit_phone(self, old_phone, new_phone):
        phone = self.find_phone(old_phone)
        if len(new_phone) != 10:
            raise ValueError
        elif phone:
            phone.value = new_phone
            return
        raise ValueError

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f'Record(Name: {self.name}, Phones: {self.phones}, Birthday: {self.birthday})'

    def __repr__(self):
        return f'Record(Name: {self.name}, Phones: {self.phones}, Birthday: {self.birthday})'


class AddressBook(UserDict):

    def add_record(self, record: Record):
        name = record.name.value
        self.data.update({name: record})

    def find(self, name):
        return self.get(name)

    def delete(self, name):
        del self[name]

    def find_next_weekday(d, weekday: int):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return d + timedelta(days=days_ahead)

    def get_upcoming_birthdays(self):
        days = 7
        today_date = datetime.today().date()
        upcoming_birthdays = []
        for el in self.data.values():
            birthday_this_year = datetime.strptime(el.birthday.value, "%d.%m.%Y").date().replace(year=today_date.year)
            if birthday_this_year < today_date:
                birthday_this_year = birthday_this_year.replace(year=today_date.year + 1)
            elif 0 <= (birthday_this_year - today_date).days <= days:
                if birthday_this_year.weekday() >= 5:
                    birthday_this_year.find_next_weekday(birthday_this_year, 0)
                congratulation_date = birthday_this_year.strftime("%d.%m.%Y")
                upcoming_birthdays.append({'Name': el.name, "Congratulation Date": congratulation_date})
        return upcoming_birthdays


def input_error_phone(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Wrong input format! Please, enter Name and 10 digit format Phone Number"
        except KeyError:
            return "Record is missing."
        except IndexError:
            return "Please, Enter Name"

    return inner


def input_error_birthday(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Wrong input format! Please, enter Name and use date format: DD.MM.YYYY."

    return inner


@input_error_phone
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error_phone
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error_phone
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        phone = record.find_phone(old_phone)
        if phone:
            record.edit_phone(old_phone, new_phone)
            message = "Phone number was changed."
        else:
            message = "Phone was not found."
            pass
    elif record is None:
        message = "Contact is missing."
    return message


@input_error_phone
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return record.phones
    else:
        return "Contact is missing."


@input_error_birthday
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday was added."
    else:
        return "Contact is mising."


@input_error_phone
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return record.birthday
    else:
        return "Contact is missing"


def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit", "quit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()