import service
from colorama import Fore
from typing import Optional, Union
from utils import Response
from form_ import UserRegisterForm


def print_response(response: Response):
    color = Fore.GREEN if response.status_code == 200 else Fore.RED
    print(color + response.data + Fore.RESET)


def login_page():
    username = input('Enter your username: ')
    password = input('Enter your password: ')
    response = service.login(username, password)
    print_response(response)


def register_page():
    username = input('Enter your username: ')
    password = input('Enter your password: ')
    form = UserRegisterForm(username, password)
    response = service.register(form)
    print_response(response)


def logout_page():
    response = service.logout()
    print_response(response)


def add_todo():
    name = input('Enter name: ')
    description = input('Enter description: ')
    response = service.todo_add(name, description)
    print_response(response)


def print_response(response: Response):
    color = Fore.GREEN if response.status_code == 200 else Fore.RED
    print(color + response.data + Fore.RESET)


def update_todo() -> None:
    todo_list = service.get_all_todos()
    if isinstance(todo_list, Response):
        return print_response(todo_list)
    print(todo_list)
    todo_id: str = input('Enter todo id you want to update: ')
    name: str = input('Enter new title: ')
    description: Optional[str] = input('Enter new description: ')
    response: Union[Response, str] = service.todo_update(name, str(todo_id), description)
    print_response(response)

def delete_todo() -> None:
    todo_list = service.get_all_todos()
    if isinstance(todo_list, Response):
        return print_response(todo_list)
    print(todo_list)
    todo_id: str = input('Enter todo id you want to delete: ')
    response: Union[Response, str] = service.todo_delete(str(todo_id))
    print_response(response)

def block_user():
    user_list = service.get_all_users()
    if isinstance(user_list, Response):
        return print_response(user_list)
    print(user_list)
    user_id = input('Enter user id you want to block; ')
    response = service.user_block(user_id)
    print_response(response)

if __name__ == '__main__':
    while True:

        choice = input('enter your choice: ')
        if choice == '1':
            login_page()
        elif choice == '2':
            register_page()
        elif choice == '3':
            logout_page()
        elif choice == '4':
            add_todo()
        elif choice == '5':
            update_todo()
        elif choice == '6':
            delete_todo() 
        elif choice == '7':
            block_user()  
        elif choice == 'q':
            break
