import requests
import json
import csv
import re
import pandas as pd

# Создадим все необходимые для запроса функции

def get_city_id(city: str, auth_data: dict) -> int:
    """
    Получает ID города по названию
    """
    url = 'https://api.vk.com/method/database.getCities'
    response = requests.get(url, params={**auth_data, 'q': city, 'need_all': 0, 'count': 1})
    if response.status_code == 200:
        return response.json()['response']['items'][0]['id']
    else:
        raise Exception(f"Ошибка при получении ID города: {response.text}")

def get_groups(city_id: int, query: str, auth_data: dict) -> list:
    """
    Получает список групп по ключевым словам
    """
    url = 'https://api.vk.com/method/groups.search'
    response = requests.get(url, params={**auth_data, 'city_id': city_id, 'q': query,
                                         'fields': 'contacts,status,description,members_count',
                                         'count': 1000, 'sort': 6})
    if response.status_code == 200:
        return response.json()['response']['items']
    else:
        raise Exception(f"Ошибка при получении списка сообществ: {response.text}")

def extract_contacts(groups: list) -> list:
    """
    Извлекает контакты из полей контактов, статуса и описания сообщества.
    
    """
    phone_pattern = r'(?:(?:8|\+7)[\- ]?)?(?:\(?\d{3}\)?[\- ]?)?\d[\d\-]{5,14}'
    email_pattern = r'[\w\.-]+@[\w\.-]+(?:\.[\w]+)+'
    contact_regex = re.compile(f"({phone_pattern}|{email_pattern})")
    
    for group in groups:
        contacts = set()
        if 'contacts' in group:
            contacts.update(contact['phone'] for contact in group['contacts'] if 'phone' in contact)
            contacts.update(contact['email'] for contact in group['contacts'] if 'email' in contact)
        
        if 'status' in group:
            contacts.update(contact_regex.findall(group['status']))
        if 'description' in group:
            contacts.update(contact_regex.findall(group['description']))
        
        group['contacts'] = ', '.join(contacts) if contacts else 'NaN'
    
    return groups

def save_to_csv(groups: list, filename: str):
    """
    Сохраняет список сообществ в CSV файл.
    """
    fieldnames = ['id', 'name', 'description', 'is_closed', 'members_count', 'contacts']
    filtered_groups = [{key: group.get(key, 'NaN') for key in fieldnames} for group in groups]
    
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_groups)

def analyze_csv(filename: str):
    """
    Анализирует CSV файл с помощью pandas, для проверки, что запрос выполнен правильно
    """
    df = pd.read_csv(filename)
    print("\nПервые 5 записей:")
    print(df.head())
    print("\nКоличество записей:", len(df))
    print("\nКоличество дубликатов:", df.duplicated().sum())

if __name__ == "__main__":
    access_token = 'MY_ACCESS_TOKEN'
    version = '5.199'
    city = 'Омск'
    key_words = 'цветы, флористика, магазин цветов'

# Используем функции для выполнения запроса

    auth_data = {'v': version, 'access_token': access_token}
    city_id = get_city_id(city, auth_data)
    groups = get_groups(city_id, key_words, auth_data)
    groups_with_contacts = extract_contacts(groups)
    save_to_csv(groups_with_contacts, 'omsk_vk_groups.csv')
    analyze_csv('omsk_vk_groups.csv')
