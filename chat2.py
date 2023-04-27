from redis_messenger import RedisMessenger
from consolemenu.items import *
from consolemenu import *
import json
import sys
import os

def check_if_logged_in(session_path: str = "session.txt"):

    if os.path.exists(session_path):
        with open(session_path, "r") as file:
            user_uuid = file.read()
            return user_uuid

    return False

def create_session(user_uuid: str, session_path: str = "session.txt"):

    with open(session_path, "w") as file:
        file.write(user_uuid)

def delete_session(session_path: str = "session.txt"):

    if os.path.exists(session_path):
        os.remove(session_path)

def clear_session_and_logout():
    delete_session()
    clear_terminal()
    sys.exit()

def authorize_user(messenger):
    '''
    This function takes care of checking if the user was previously logged
    in by using session.txt.
    '''

    # Check if user was already logged in
    in_loop = True
    user_uuid = ""
    while in_loop:
        user_uuid = check_if_logged_in()
        if not user_uuid:
            print("Provide your uuid or write \"new\" to automatically create a new account:")
            answer = input()
            if answer == "new":
                username = input("Username: ")
                user_uuid = messenger.create_user(username=username)
                create_session(user_uuid)
                in_loop = False
            else:
                exists = messenger.check_user_exists(answer)
                if exists:
                    create_session(answer)
                    print("You are now logged in.")
                    user_uuid = answer
                    in_loop = False
                else:
                    print("User does not exist.")
        else:
            in_loop = False

    return user_uuid

def main():

    messenger = RedisMessenger()
    user_id = authorize_user(messenger)    

    clear_terminal()
    menu = ConsoleMenu("Chat - You are logged in with session.txt", f"Your token: {user_id}")
    
    contacts = [c['username'] for c in messenger.list_contacts(user_id)]
    contacts_submenu = ["Add contact", "Remove contact"]

    for c in contacts:
        contacts_submenu.append(c)

    contacts_submenu.append(FunctionItem("test", sys.exit))

    selection_menu = SelectionMenu(contacts_submenu)
    submenu_item = SubmenuItem("My contacts", selection_menu, menu)
    menu.append_item(submenu_item)

    clear_session = FunctionItem("Clear session and logout", clear_session_and_logout)
    menu.append_item(clear_session)

    menu.show()

if __name__ == "__main__":
    main()