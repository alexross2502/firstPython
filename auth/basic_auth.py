import requests
import logging

def login_with_basic_auth(base_url, basic_auth_user, basic_auth_pass):
    session = requests.Session()
    session.auth = (basic_auth_user, basic_auth_pass)
    response = session.get(base_url, timeout=5, verify=False)
    if response.status_code == 200:
        logging.info(f"Успешная авторизация через Basic Auth на сайте: {base_url}")
        return session
    else:
        logging.error(f"Не удалось выполнить авторизацию через Basic Auth на сайте: {base_url}")
        return None
