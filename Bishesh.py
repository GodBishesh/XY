import requests
from getpass import getpass
from collections import deque
import logging
from rich.console import Console
from rich.table import Table

logging.basicConfig(filename="brute.log", level=logging.INFO)

console = Console()
credentials = deque()

class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name.lower()

def get_friends_list(api_token):
    try:
        session = requests.Session()
        session.headers.update({'Authorization': f'Bearer {api_token}'})
        username = session.get('https://graph.facebook.com/v1.0/me?access_token='+api_token).json()['name']
        friends = f"https://graph.facebook.com/v1.0/{username}/friends?access_token="+api_token
        response = session.get(friends).json()
        print(f"Fetched {len(response)} friends for {username}")
        return [User(i['id'], i['name']) for i in response]
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

def display_menu():
    print("1. Login through Facebook API")
    print("2. Logout")
    print("3. Crack Public Profile (Fetch Friend List and Attempt Passwords)")
    print("4. Exit")

def login(api_token):
    friends = get_friends_list(api_token)
    if friends:
        print("Logged in successfully.")
    else:
        print("Login failed. Please check your API token.")
    return friends, api_token

def logout(friends, api_token):
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {api_token}'})
    logout_status = session.delete(f"https://graph.facebook.com/{api_token}")
    if logout_status.ok:
        return None, None
    else:
        print("Logout failed. Please try again.")
        return friends, api_token

def crack_public_profile(friends):
    if friends is not None:
        username_list = [f.username for f in friends]
        for username in username_list:
            for password_suffix in [123, 1234, 12345]:
                password = username + str(password_suffix)
                print(f"Attempting with username: {username}, password: {password}")
    else:
        print("You need to login first.")

def main():
    friends = None
    api_token = None

    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            if api_token is None:
                api_token = getpass("Facebook API Token: ")
                friends, api_token = login(api_token)
            else:
                print("You're already logged in.")
        elif choice == "2":
            if api_token is not None:
                friends, api_token = logout(friends, api_token)
            else:
                print("You are not logged in yet.")
        elif choice == "3":
            crack_public_profile(friends)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
