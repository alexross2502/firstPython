import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

class Authenticator:
    def __init__(self):
        self.login_url = os.getenv("LOGIN_URL")
        self.submit_login_url = os.getenv("SUBMIT_LOGIN_URL")
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        self.session = requests.Session()

    def get_csrf_token(self):
        response = self.session.get(self.login_url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token_input = soup.find('input', {'name': '_token'}) 
        if not csrf_token_input: csrf_token_input = soup.find('input', {'name': '_csrf_token'})
        if csrf_token_input:
            return csrf_token_input['value']
        else:
            print("CSRF token not found. Here's the HTML of the login page for debugging:")
            print(response.text)
            return None

    def login(self):
        csrf_token = self.get_csrf_token()
        if not csrf_token:
            print("Failed to retrieve CSRF token.")
            return None
        login_data = {
            '_token': csrf_token,
            'terms[email]': self.username,
            'terms[password]': self.password,
            'remember': '1',
            'btnLogin': 'LOGIN'
        }
        response = self.session.post(self.submit_login_url, data=login_data, verify=False)
        if response.status_code in [200, 302]: 
            print("Login successful")
            return self.session
        else:
            print(f"Login failed: Status code {response.status_code}")
            print(response.text)
            return None

if __name__ == "__main__":
    auth = Authenticator()
    session = auth.login()
    if session:
        print("Session established")
    else:
        print("Failed to establish session")
