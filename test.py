import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL_ORIGINAL = os.getenv('BASE_URL_ORIGINAL')
BASE_URL_COPY = os.getenv('BASE_URL_COPY')

def read_urls_from_txt(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        urls = [line.strip() for line in file if line.strip()]
    return urls

def check_urls(base_url, relative_urls):
    non_200_urls = []
    for relative_url in relative_urls:
        full_url = f"{base_url}{relative_url}"
        response = requests.get(full_url)
        print(f"URL: {full_url} - Status Code: {response.status_code}")
        if response.status_code != 200:
            non_200_urls.append(full_url)
    return non_200_urls

def save_urls_to_txt(urls, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(url + '\n')

if __name__ == "__main__":
    same_links_file = "same_links.txt"
    output_non_200_file = "non_200_urls.txt"

    relative_urls = read_urls_from_txt(same_links_file)

    non_200_urls_original = check_urls(BASE_URL_ORIGINAL, relative_urls)

    non_200_urls_copy = check_urls(BASE_URL_COPY, relative_urls)

    all_non_200_urls = non_200_urls_original + non_200_urls_copy

    save_urls_to_txt(all_non_200_urls, output_non_200_file)

    print(f"URL с кодом ответа не 200 сохранены в {output_non_200_file}")
