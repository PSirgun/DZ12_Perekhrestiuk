from collections import UserDict
from datetime import datetime
from pathlib import Path
import pprint
import pickle
import re

# class block ----------------------------------------------------------------

class MyError(Exception):
    pass

class MyError2(Exception):
    pass


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)  
        self.value = value 

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        new_value = ''.join(re.findall('\d+', new_value))  
        if len(new_value) != 10 or not new_value.isdigit():
            raise MyError
        self._value = new_value

    def __str__(self):
        return self._value

class Record:
    
    def __init__(self, name): 
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        

    def add_phone(self, phone):
        if phone not in [p for p in self.phones]:
            self.phones.append(phone)
        else:
            raise MyError
    
    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone.value:
                del self.phones[self.phones.index(p)]
            else:
                raise MyError2
            
    def edit_phone(self, old_phone, new_phone):
        
        for i, phone in enumerate(self.phones):
            if phone == old_phone:
                self.phones[i] = new_phone
                return
            raise ValueError

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
            
    def add_bd(self, bd):
        self.birthday = bd
    
    def days_to_birthday(self):
        today = datetime.today().date()
        next_bd = self.birthday.value.replace(year=today.year)
        next_bd = next_bd.date()
        if next_bd < today:
            next_bd = next_bd.replace(year=today.year + 1)
        
        days_left = (next_bd - today).days

        return days_left
       
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p for p in self.phones)}"

class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.lines = 2


   
   
    def add_record(self, contact: Record):
        self.data[contact.name.value] = contact
        self.keys = list(self.data.keys())
        self.lines = "2"

    def find(self, name):
        if name:
            return self.data.get(name)
        return

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def __iter__(self):
        for contact in self.data:
            yield {"name":self.data[contact].name.value, "phones":self.data[contact].phones, "birthday":self.data[contact].birthday}

    # def __iter__(self):
    #     self.index = 0
    #     return self

    # def __next__(self):  
    #     if self.index < len(self.keys):
    #         key = self.keys[self.index]
    #         self.index += 1
    #         x = {"name":self.data[key].name.value, "phones":self.data[key].phones, "birthday":self.data[key].birthday}
    #         return x
    #     else:
    #         raise StopIteration
    
    def iterator(self, lines):
        if lines == None:
            lines = self.lines
        else:
            self.lines = lines
        count = 0
        
        page = []
        for i in phone_book:
            page.append(i)
            count += 1
            if count == lines:        
                yield page
                page = []  
                count = 0       
        if page:
            yield page

    def save_data(self):
        file_name = 'data.bin'
        with open(file_name, 'wb') as fh:
            pickle.dump(self.data, fh)

    def load_data(self):
        file_name = 'data.bin'
        if Path(file_name).is_file():
            with open(file_name, 'rb') as fh:
                self.data = pickle.load(fh)
        else:
            print ('"data.bin" has not loaded')
            return 

class Birthday:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        new_value = str(new_value)
        new_value = re.findall(r"\d+", new_value)
        new_value = " ".join(i for i in new_value)
        new_value = datetime.strptime(new_value, '%d %m %Y')
        self._value = new_value

    def __repr__(self):
        return self.value.strftime('%Y-%m-%d')    
    
    def __iter__(self):
        yield self._value.strftime('%Y-%m-%d') 
#end class block -------------------------------------------------------------------- decorators block

phone_book = AddressBook()

def decor_func(func):
    def inner(*args):
        try:
            return func(*args)
        except IndexError:
            return "Not enough arguments"
        except KeyError:
            return "Name not in phone book"
        except TypeError:
                return "Too much arguments"
        except ValueError:
            return "Invalid format"
        except AttributeError:
            return "Name not in phone book"
        except MyError:
            return "Phone already in phone book"
        except MyError2:
            return "Phone not in phone book"
    return inner


def decor_change(func):
    def inner(*args):
        try:
            return func(*args)
        except IndexError:
            return "Not enough arguments"
        except TypeError:
            return "No one argument"
        except ValueError:
            return "Incorrect phone number"
        except AttributeError:
            return "Name not in phone book"
    return inner

#  end decorators block ----------------------------------------------------------------- sub block

@decor_func
def sub_add(*args):
    name = Name(args[0]).value
    phone = Phone(args[1]).value
    if phone_book.find(name):
        contact = phone_book[name]
        contact.add_phone(phone)
    else:
        contact = Record(name)
        contact.add_phone(phone)
        phone_book.add_record(contact) 
    return f" Added {name} - {phone} to phone book "


@decor_func
def sub_show(*args):
    for page in phone_book.iterator(int(args[1]) if args else None):
        for line in page:
            print (line)
        print ('End page \n')    
            
    return "End phone book"

@decor_func
def sub_part_show(*args):
    args = list(args)
    if args[0] == '':
        del args[0]
    contact_list = []
    for data in phone_book:
        for v in data.values():
            if v and (args[0] in v or any(args[0] in str(value) for value in v)):
                contact_list.append(data)
                break

    pprint.pprint(contact_list, sort_dicts=False)
    return "ok"

@decor_change
def sub_change(*args):
    contact = phone_book.find(args[0]) 
    contact.edit_phone(args[1], args[2])
    return f" For {args[0]} changed {Phone(args[1])} to {args[2]}"

@decor_func 
def sub_phone(*args):
    contact = phone_book.find(args[0].title()) 
    return (f'{contact}')
    
@decor_func
def sub_hello():
    return "How can I help you?"

@decor_func
def sub_exit():
    return "Good bye!"

@decor_func
def sub_delete(*args):
    if args[0].title() in phone_book:
        phone_book.delete(args[0].title())
        return f'{args[0]} deleted from phone book'
    raise KeyError

@decor_func
def sub_remove_phone(*args):
    phone = Phone(args[1])
    contact = phone_book.find(args[0].title()) 
    contact.remove_phone(phone)
    return f"For {args[0]} phone number {phone} removed"

@decor_func
def sub_add_birthday(*args):
    name = Name(args[0]).value
    bd = Birthday(args[1:])
    if phone_book.find(name):
        contact = phone_book[name]
        contact.add_bd(bd)
    else:
        contact = Record(name)
        contact.add_bd(bd)
        phone_book.add_record(contact) 
    return f" For {name} added birthday {bd.value.strftime('%d %m %Y')} to phone book "

@decor_func
def sub_days_to_bd(*args):
    name = Name(args[0]).value
    contact = phone_book[name]
    days = contact.days_to_birthday()
    return f"{days} days to {name}'s birthday"



OPERATIONS = {
    sub_days_to_bd : ("bd?",),
    sub_remove_phone : ("remove phone",),
    sub_delete : ("delete", ),
    sub_hello : ("hello",), 
    sub_change : ("change",),
    sub_phone : ("phone",),
    sub_show : ("show all",),
    sub_add_birthday: ("bd", "birthday"),
    sub_exit: ("good bye", "close", "exit", "."),
    sub_add : ("add",),
    sub_part_show : ("search",'find'),
}
# end sub block -------------------------------------------------------------------------------- func. block

def sanit_name(*args):
    ful_name = ""
    args = list(args)
    for i in args:
        if re.search(r'^[a-zA-Z]+$', i):
            ful_name += i + ' '       
        else:
            args = args[args.index(i):]
            args.insert(0, ful_name.strip().title())
            break
    return args

def main():
    
    phone_book.load_data()
    while True:
        user_input = input(">>> ")
        command_found = False        
        for sub_f, command  in OPERATIONS.items():
            if command_found:
                break 
            for com in command:
                if user_input.casefold().startswith(com):
                    user_args = sanit_name(*user_input[len(com):].strip().split())
                    print(sub_f(*user_args))
                    if sub_f == sub_exit:
                        phone_book.save_data()
                        return
                    command_found = True
                    break
        if not command_found:       
            print("Command not found")

if __name__ == '__main__':
    main() 





