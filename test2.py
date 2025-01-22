import requests
from bs4 import BeautifulSoup
import json
from requests.auth import HTTPBasicAuth

def get_description(url, auth):
    try:
        response = requests.get(url, auth=auth, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Предполагаем, что описание находится в теге <meta name="description">
        description_tag = soup.find('meta', attrs={'name': 'description'})
        if description_tag and 'content' in description_tag.attrs:
            return description_tag['content']
        else:
            return "No description available"
    except Exception as e:
        return f"Error fetching description: {e}"

def process_links(file_path, base_url, auth):
    results = []

    with open(file_path, 'r') as file:
        links = file.readlines()

    for link in links:
        link = link.strip()  # Удаляем пробелы и переносы строк
        full_url = base_url + link
        description = get_description(full_url, auth)
        results.append({
            'url': full_url,
            'description': description
        })

    return results

def save_to_json(data, output_file):
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    base_url = "https://localhost:8000/"
    input_file = 'extracted_links.txt'
    output_file = 'resulttest.json'
    
    # Укажите ваши данные для авторизации
    username = 'your_username'
    password = 'your_password'
    auth = HTTPBasicAuth(username, password)
    
    links_data = process_links(input_file, base_url, auth)
    save_to_json(links_data, output_file)
    print(f"Processed links saved to {output_file}")