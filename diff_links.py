import re
from urllib.parse import urlparse

def normalize_url_for_comparison(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.replace('www2.', 'www.')
    return f"{parsed_url.scheme}://{netloc}{parsed_url.path}?{parsed_url.query}" if parsed_url.query else f"{parsed_url.scheme}://{netloc}{parsed_url.path}"

def read_urls_from_txt(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        urls = set(line.strip() for line in file if line.strip())
    return urls

def compare_txt_files(file1, file2, output_same, output_different):
    urls_file1 = read_urls_from_txt(file1)
    urls_file2 = read_urls_from_txt(file2)

    normalized_urls_file1 = {url: normalize_url_for_comparison(url) for url in urls_file1}
    normalized_urls_file2 = {url: normalize_url_for_comparison(url) for url in urls_file2}

    same_links = {url for url, norm_url in normalized_urls_file1.items() if norm_url in normalized_urls_file2.values()}
    different_links = {url for url, norm_url in normalized_urls_file1.items() if norm_url not in normalized_urls_file2.values()}
    different_links.update(url for url, norm_url in normalized_urls_file2.items() if norm_url not in normalized_urls_file1.values())

    with open(output_same, 'w', encoding='utf-8') as file:
        for link in same_links:
            file.write(link + '\n')

    with open(output_different, 'w', encoding='utf-8') as file:
        for link in different_links:
            file.write(link + '\n')

    print(f"Файл с одинаковыми ссылками: {output_same}")
    print(f"Файл с различными ссылками: {output_different}")

if __name__ == "__main__":
    file1 = "original_links.txt"
    file2 = "copy_links.txt"
    output_same = "same_links.txt"
    output_different = "different_links.txt"

    compare_txt_files(file1, file2, output_same, output_different)
