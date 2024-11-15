import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import time
from dotenv import load_dotenv
import os
import auth  

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
            print(f"Error fetching {url}: Status code {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
        return None

    def parse_links(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href")
            url = urljoin(base_url, href)
            if self.is_valid_url(url):
                links.add(url)
        return links

    def is_valid_url(self, url):
        parsed = urlparse(url)
        if any(exclude in url for exclude in ["/assets", "/_profiler", "/uploads", "/independent-female-escorts"]):
            return False
        return parsed.netloc == urlparse(self.base_url).netloc and url not in self.visited

    def crawl(self, url):
        print(f"Crawling: {url}")
        self.visited.add(url)
        page_content = self.fetch_page(url)
        if page_content:
            self.sitemap_urls.append(url)
            links = self.parse_links(page_content, url)
            for link in links:
                if link not in self.visited:
                    time.sleep(0.5)
                    self.crawl(link)

    def generate_sitemap(self):
        urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        for url in self.sitemap_urls:
            url_tag = ET.SubElement(urlset, "url")
            loc = ET.SubElement(url_tag, "loc")
            loc.text = url
        tree = ET.ElementTree(urlset)
        tree.write("sitemap.xml", encoding="utf-8", xml_declaration=True)
        print("Sitemap generated: sitemap.xml")

    def run(self):
        self.crawl(self.base_url)
        self.generate_sitemap()

if __name__ == "__main__":
    base_url = os.getenv("BASE_URL")

    auth = auth.Authenticator()
    session = auth.login()
    if session:
        generator = SitemapGenerator(base_url, session)
        generator.run()
