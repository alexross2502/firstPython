import xml.etree.ElementTree as ET

def extract_links_from_sitemap(file_path, base_url):
    # Чтение XML-контента из локального файла sitemap
    with open(file_path, 'r') as file:
        sitemap_content = file.read()

    # Парсим XML-контент
    root = ET.fromstring(sitemap_content)
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    
    # Извлекаем все ссылки
    links = []
    for url in root.findall('ns:url', namespace):
        loc = url.find('ns:loc', namespace).text
        if loc.startswith(base_url):
            # Обрезаем начало ссылки
            trimmed_link = loc[len(base_url):]
            links.append(trimmed_link.lstrip('/'))

    return links

def save_links_to_file(links, filename):
    with open(filename, 'w') as file:
        for link in links:
            file.write(link + '\n')

if __name__ == '__main__':
    file_path = 'sitemap.xml'
    base_url = 'https://www.pvssy.com/'

    links = extract_links_from_sitemap(file_path, base_url)
    save_links_to_file(links, 'extracted_links.txt')

    print(f"Extracted {len(links)} links and saved to 'extracted_links.txt'")