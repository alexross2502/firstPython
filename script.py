import time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import requests
import os
from dotenv import load_dotenv
import urllib3
from auth.basic_auth import login_with_basic_auth
from auth.form_auth import login_with_form_auth

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
        if any(exclude in url for exclude in ["/assets", "/_profiler", "/uploads", "/independent-female-escorts", "cdn-cgi", "page", "my-advertisement-delete"]) or parsed.fragment:
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

    def run(self, output_filename, additional_urls=None):
        if additional_urls:
            for url in additional_urls:
                self.visited.add(url)
                self.crawl(url)
        self.crawl(self.base_url)
        self.generate_sitemap(output_filename)

def generate_sitemap_for_site(base_url, login_url_suffix, basic_auth_user, basic_auth_pass, form_username, form_password, output_filename, site_type, additional_urls=None):
    session = login_with_basic_auth(base_url, basic_auth_user, basic_auth_pass)
    if session:
        login_url = base_url + login_url_suffix
        session = login_with_form_auth(login_url, session, form_username, form_password, site_type, base_url)
        if session:
            generator = SitemapGenerator(base_url, session)
            generator.run(output_filename, additional_urls=additional_urls)
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
    additional_urls_original = os.getenv("ADDITIONAL_URLS_ORIGINAL").split(',')

    base_url_copy = os.getenv("BASE_URL_COPY")
    output_filename2 = "sitemap_copy.xml"
    site_type_copy = "copy"

    login_url_suffix = "login"

    generate_sitemap_for_site(base_url_original, login_url_suffix, basic_auth_user, basic_auth_pass, form_username, form_password, output_filename1, site_type_original, additional_urls=additional_urls_original)
    generate_sitemap_for_site(base_url_copy, login_url_suffix, basic_auth_user, basic_auth_pass, form_username, form_password, output_filename2, site_type_copy)
