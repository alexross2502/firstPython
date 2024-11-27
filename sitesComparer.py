import os
import requests
import json
import logging
from lxml import html
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

BASE_URL_ORIGINAL = os.getenv('BASE_URL_ORIGINAL')
BASE_URL_COPY = os.getenv('BASE_URL_COPY')
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER")
BASIC_AUTH_PASS = os.getenv("BASIC_AUTH_PASS")
FORM_USERNAME = os.getenv("FORM_USERNAME")
FORM_PASSWORD = os.getenv("FORM_PASSWORD")
LOGIN_URL_SUFFIX = os.getenv("LOGIN_URL_SUFFIX", "login")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelение)s - %(message)s', filename='script.log', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelение)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def clean_string(value):
    return value.replace('\n', ' ').replace('"', '\\"').strip()

def extract_data(session, url):
    response = session.get(url)
    tree = html.fromstring(response.content)

    title = tree.xpath('string(//title)')
    description = tree.xpath('string(//meta[@name="description"]/@content)')
    keywords = tree.xpath('string(//meta[@name="keywords"]/@content)')
    h1 = tree.xpath('string(//h1[contains(@class, "text-center")])')
    article = tree.xpath('string((//div[@class="hArticle"])[last()])')

    data = {
        "url": url,
        "title": clean_string(title),
        "description": clean_string(description),
        "keywords": clean_string(keywords),
        "h1": clean_string(h1),
        "article": clean_string(article)
    }
    return data

def compare_data(data1, data2):
    differences = {}
    for key in data1:
        if data1[key] != data2[key]:
            differences[key] = {"original": data1[key], "copy": data2[key]}
    return differences

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

def main(input_file, output_file):
    result = []

    session_original = login_with_basic_auth(BASE_URL_ORIGINAL, BASIC_AUTH_USER, BASIC_AUTH_PASS)
    if session_original:
        login_url_original = BASE_URL_ORIGINAL + LOGIN_URL_SUFFIX
        session_original = login_with_form_auth(login_url_original, session_original, FORM_USERNAME, FORM_PASSWORD, "original", BASE_URL_ORIGINAL)

    session_copy = login_with_basic_auth(BASE_URL_COPY, BASIC_AUTH_USER, BASIC_AUTH_PASS)
    if session_copy:
        login_url_copy = BASE_URL_COPY + LOGIN_URL_SUFFIX
        session_copy = login_with_form_auth(login_url_copy, session_copy, FORM_USERNAME, FORM_PASSWORD, "copy", BASE_URL_COPY)

    if not session_original or not session_copy:
        logging.error("Не удалось выполнить авторизацию на одном из сайтов")
        return

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            path = line.strip()
            url1 = f"{BASE_URL_ORIGINAL}{path}"
            url2 = f"{BASE_URL_COPY}{path}"

            logging.info("Processing URL1: %s", url1)
            data1 = extract_data(session_original, url1)
            logging.info("Processing URL2: %s", url2)
            data2 = extract_data(session_copy, url2)

            differences = compare_data(data1, data2)

            if differences:
                logging.info("Differences found for %s: %s", path, json.dumps(differences, ensure_ascii=False, indent=2))
                result.append({
                    "path": path,
                    "differences": differences
                })

    with open(output_file, 'w', encoding='utf-8') as output:
        json.dump(result, output, ensure_ascii=False, indent=2)

    logging.info("Processing complete. Result saved to %s", output_file)

if __name__ == "__main__":
    input_file = "same_links.txt"
    output_file = "differences_result.json"
    logging.info("Starting script execution")
    main(input_file, output_file)
    logging.info("Script execution completed")
