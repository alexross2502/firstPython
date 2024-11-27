import xml.etree.ElementTree as ET
import re
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

if __name__ == "__main__":
    sitemap_original = "sitemap_original.xml"
    sitemap_copy = "sitemap_copy.xml"
    output_original = "original_links.txt"
    output_copy = "copy_links.txt"

    original_urls = extract_urls_from_sitemap(sitemap_original)
    copy_urls = extract_urls_from_sitemap(sitemap_copy)

    save_urls_to_txt(original_urls, output_original)
    save_urls_to_txt(copy_urls, output_copy)

    print(f"Ссылки из {sitemap_original} сохранены в {output_original}")
    print(f"Ссылки из {sitemap_copy} сохранены в {output_copy}")
