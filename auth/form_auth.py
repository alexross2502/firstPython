import requests
from bs4 import BeautifulSoup
import logging

def login_with_form_auth(login_url, session, form_username, form_password, site_type, base_url):
    login_page = session.get(login_url, timeout=5, verify=False)
    soup = BeautifulSoup(login_page.text, 'html.parser')

    csrf_token = None
    login_data = {}
    submit_url = login_url

    if site_type == "original":
        csrf_token = soup.find("input", {"name": "_token"})
        if csrf_token:
            csrf_token = csrf_token["value"]
            login_data = {
                '_token': csrf_token,
                'terms[email]': form_username,
                'terms[password]': form_password,
                'remember': 1,
                'btnLogin': 'LOGIN'
            }
            submit_url = base_url + "submitLogin"
        else:
            logging.error("CSRF-токен не найден на странице входа (%s): %s", site_type, login_url)
            return None
    elif site_type == "copy":
        csrf_token = soup.find("input", {"name": "_csrf_token"})
        if csrf_token:
            csrf_token = csrf_token["value"]
            login_data = {
                '_csrf_token': csrf_token,
                '_target_path': '/my-account',
                '_username': form_username,
                '_password': form_password
            }
        else:
            logging.error("CSRF-токен не найден на странице входа (%s): %s", site_type, login_url)
            return None

    response = session.post(submit_url, data=login_data, timeout=5, verify=False)
    if response.status_code == 200:
        logging.info("Успешная авторизация через форму входа на сайте (%s): %s", site_type, submit_url)
        return session
    else:
        logging.error("Не удалось выполнить авторизацию через форму входа на сайте (%s): %s, код состояния %d", site_type, submit_url, response.status_code)
        return None
