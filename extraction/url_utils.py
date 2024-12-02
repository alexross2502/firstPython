import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs, urlencode

def normalize_url(url):
    url = re.sub(r' ', '%20', url)
    parsed_url = urlparse(url)
    path = parsed_url.path.lstrip('/')
    query_params = parse_qs(parsed_url.query)

    if 'type' in query_params:
        del query_params['type']

    normalized_query = urlencode(query_params, doseq=True)
    return f"{path}?{normalized_query}".rstrip('?') if normalized_query else path

def extract_urls_from_sitemap(sitemap_file):
    tree = ET.parse(sitemap_file)
    root = tree.getroot()
    urls = set()
    for url in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
        normalized_loc = normalize_url(loc)
        urls.add(normalized_loc)
    return urls

def save_urls_to_txt(urls, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(url + '\n')
