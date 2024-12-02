import os
import requests
import json
import logging
from lxml import html
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from auth.basic_auth import login_with_basic_auth
from auth.form_auth import login_with_form_auth

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
    soup = BeautifulSoup(response.content, 'html.parser')

    title = tree.xpath('string(//title)')
    description = tree.xpath('string(//meta[@name="description"]/@content)')
    keywords = tree.xpath('string(//meta[@name="keywords"]/@content)')
    h1 = tree.xpath('string(//h1[contains(@class, "text-center")])')
    article = tree.xpath('string((//div[@class="hArticle"])[last()])')

    meta_robots = tree.xpath('string(//meta[@name="robots"]/@content)')
    meta_charset = tree.xpath('string(//meta[@charset]/@charset)')
    h2 = tree.xpath('string(//h2)')
    h3 = tree.xpath('string(//h3)')
    canonical = tree.xpath('string(//link[@rel="canonical"]/@href)')
    og_title = tree.xpath('string(//meta[@property="og:title"]/@content)')
    og_description = tree.xpath('string(//meta[@property="og:description"]/@content)')
    twitter_card = tree.xpath('string(//meta[@name="twitter:card"]/@content)')
    structured_data = soup.find('script', type='application/ld+json')

    data = {
        "url": url,
        "title": clean_string(title),
        "description": clean_string(description),
        "keywords": clean_string(keywords),
        "h1": clean_string(h1),
        "article": clean_string(article),
        "meta_robots": clean_string(meta_robots),
        "meta_charset": clean_string(meta_charset),
        "h2": clean_string(h2),
        "h3": clean_string(h3),
        "canonical": clean_string(canonical),
        "og_title": clean_string(og_title),
        "og_description": clean_string(og_description),
        "twitter_card": clean_string(twitter_card),
        "structured_data": clean_string(structured_data.string if structured_data else "")
    }
    return data

def compare_data(data1, data2):
    differences = {}
    for key in data1:
        if data1[key] != data2[key]:
            differences[key] = {"original": data1[key], "copy": data2[key]}
    return differences

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
