import time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import requests
import os
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class SitemapGenerator:
    def __init__(self, base_url, session):
        self.base_url = base_url if base_url.endswith('/') else base_url + '/'
        self.visited = set()
        self.sitemap_urls = []
        self.session = session

    def fetch_page(self, url):
        try:
            response = self.session.get(url, timeout=5, verify=False)
            if response.status_code == 200:
                return response.text
            print(f"Ошибка при получении {url}: код состояния {response.status_code}")
        except requests.RequestException as e:
            print(f"Ошибка при получении {url}: {e}")
        return None

    def parse_links(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href").strip()
            url = urljoin(base_url, href)
            if self.is_valid_url(url):
                links.add(url)
        return links

    def is_valid_url(self, url):
        parsed = urlparse(url)
        if any(exclude in url for exclude in ["/assets", "/_profiler", "/uploads", "/independent-female-escorts", "cdn-cgi", "page", "categories", "my-advertisement-delete"]) or parsed.fragment:
            return False
        return parsed.netloc == urlparse(self.base_url).netloc and url not in self.visited

    def crawl(self, url):
        print(f"Обход: {url}")
        self.visited.add(url)
        page_content = self.fetch_page(url)
        if page_content:
            self.sitemap_urls.append(url)
            links = self.parse_links(page_content, url)
            for link in links:
                if link not in self.visited:
                    time.sleep(0.5)
                    self.crawl(link)

    def generate_sitemap(self, output_filename):
        urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        for url in self.sitemap_urls:
            url_tag = ET.SubElement(urlset, "url")
            loc = ET.SubElement(url_tag, "loc")
            loc.text = url
        tree = ET.ElementTree(urlset)
        tree.write(output_filename, encoding="utf-8", xml_declaration=True)
        print(f"Карта сайта сгенерирована: {output_filename}")

    def run(self, output_filename, additional_url=None):
        if additional_url:
            self.visited.add(additional_url)
            self.crawl(additional_url)
        self.crawl(self.base_url)
        self.generate_sitemap(output_filename)

def login_with_basic_auth(base_url, basic_auth_user, basic_auth_pass):
    session = requests.Session()
    session.auth = (basic_auth_user, basic_auth_pass)
    response = session.get(base_url, timeout=5, verify=False)
    if response.status_code == 200:
        print(f"Успешная авторизация через Basic Auth на сайте: {base_url}")
        return session
    else:
        print(f"Не удалось выполнить авторизацию через Basic Auth на сайте: {base_url}")
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
            print(f"CSRF-токен не найден на странице входа ({site_type}): {login_url}")
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
            print(f"CSRF-токен не найден на странице входа ({site_type}): {login_url}")
            return None

    response = session.post(submit_url, data=login_data, timeout=5, verify=False)
    if response.status_code == 200:
        print(f"Успешная авторизация через форму входа на сайте ({site_type}): {submit_url}")
        return session
    else:
        print(f"Не удалось выполнить авторизацию через форму входа на сайте ({site_type}): {submit_url}, код состояния {response.status_code}")
        return None

def generate_sitemap_for_site(base_url, login_url_suffix, basic_auth_user, basic_auth_pass, form_username, form_password, output_filename, site_type, additional_url=None):
    session = login_with_basic_auth(base_url, basic_auth_user, basic_auth_pass)
    if session:
        login_url = base_url + login_url_suffix
        session = login_with_form_auth(login_url, session, form_username, form_password, site_type, base_url)
        if session:
            generator = SitemapGenerator(base_url, session)
            generator.run(output_filename, additional_url=additional_url)
        else:
            print(f"Не удалось выполнить авторизацию через форму входа на сайте ({site_type})")
    else:
        print(f"Не удалось выполнить авторизацию через Basic Auth на сайте ({site_type})")

if __name__ == "__main__":
    basic_auth_user = os.getenv("BASIC_AUTH_USER")
    basic_auth_pass = os.getenv("BASIC_AUTH_PASS")
    form_username = os.getenv("FORM_USERNAME")
    form_password = os.getenv("FORM_PASSWORD")

    base_url_original = os.getenv("BASE_URL_ORIGINAL")
    output_filename1 = "sitemap_original.xml"
    site_type_original = "original"
    additional_url_original = "https://www.pvssy.com/all-country?type=Female%20Strippers"

    base_url_copy = os.getenv("BASE_URL_COPY")
    output_filename2 = "sitemap_copy.xml"
    site_type_copy = "copy"

    login_url_suffix = "login"

    generate_sitemap_for_site(base_url_original, login_url_suffix, basic_auth_user, basic_auth_pass, form_username, form_password, output_filename1, site_type_original, additional_url=additional_url_original)

    generate_sitemap_for_site(base_url_copy, login_url_suffix, basic_auth_user, basic_auth_pass, form_username, form_password, output_filename2, site_type_copy)
