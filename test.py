import os
import requests
import json
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from auth.basic_auth import login_with_basic_auth
from auth.form_auth import login_with_form_auth

# Загрузка переменных окружения
load_dotenv()

# Константы для URL и авторизации
BASE_URL_ORIGINAL = os.getenv('BASE_URL_ORIGINAL')
BASE_URL_COPY = os.getenv('BASE_URL_COPY')
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER")
BASIC_AUTH_PASS = os.getenv("BASIC_AUTH_PASS")
FORM_USERNAME = os.getenv("FORM_USERNAME")
FORM_PASSWORD = os.getenv("FORM_PASSWORD")
LOGIN_URL_SUFFIX = os.getenv("LOGIN_URL_SUFFIX", "login")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(level)s - %(message)s', filename='script.log', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(level)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def clean_string(value):
    """Функция для очистки строк от лишних символов"""
    return value.replace('\n', ' ').replace('"', '\\"').strip()

def extract_description(session, url):
    """Функция для извлечения description с сайта"""
    response = session.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Извлечение description
    description = soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else ''
    
    return clean_string(description)

def main(input_file, output_file):
    result = []

    # Логин на оригинальном сайте
    session_original = login_with_basic_auth(BASE_URL_ORIGINAL, BASIC_AUTH_USER, BASIC_AUTH_PASS)
    if session_original:
        login_url_original = BASE_URL_ORIGINAL + LOGIN_URL_SUFFIX
        session_original = login_with_form_auth(login_url_original, session_original, FORM_USERNAME, FORM_PASSWORD, "original", BASE_URL_ORIGINAL)

    # Логин на копии сайта
    session_copy = login_with_basic_auth(BASE_URL_COPY, BASIC_AUTH_USER, BASIC_AUTH_PASS)
    if session_copy:
        login_url_copy = BASE_URL_COPY + LOGIN_URL_SUFFIX
        session_copy = login_with_form_auth(login_url_copy, session_copy, FORM_USERNAME, FORM_PASSWORD, "copy", BASE_URL_COPY)

    if not session_original or not session_copy:
        logging.error("Не удалось выполнить авторизацию на одном из сайтов")
        return

    # Чтение входного файла и обработка ссылок
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            path = line.strip()
            if 'location' in path:
                url1 = f"{BASE_URL_ORIGINAL}{path}"
                url2 = f"{BASE_URL_COPY}{path}"

                logging.info("Processing URL1: %s", url1)
                description1 = extract_description(session_original, url1)
                logging.info("Processing URL2: %s", url2)
                description2 = extract_description(session_copy, url2)

                result.append({
                    "path": path,
                    "original_description": description1,
                    "copy_description": description2
                })

    # Запись результата в выходной файл
    with open(output_file, 'w', encoding='utf-8') as output:
        json.dump(result, output, ensure_ascii=False, indent=2)

    logging.info("Processing complete. Result saved to %s", output_file)

if __name__ == "__main__":
    input_file = "same_links.txt"
    output_file = "test_result.json"
    logging.info("Starting script execution")
    main(input_file, output_file)
    logging.info("Script execution completed")