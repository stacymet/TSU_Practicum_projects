import requests
import csv
from datetime import datetime

VACANCIES_URL = 'https://api.superjob.ru/2.0/vacancies/'
SECRET_KEY = ''

headers = {'X-Api-App-Id': SECRET_KEY}
params = {
    'keyword' : 'Аналитик',
    'period' : 7,
    'count' : 100
}

response = requests.get(VACANCIES_URL, headers=headers, params=params)

if response.status_code == 200:
    data_vacancies = response.json()
    vacancies_analytics = []
    for vacancy in data_vacancies.get('objects', []):
        timestamp = vacancy.get('date_published')
        vacancies_analytics.append({
            'Ссылка на вакансию': vacancy.get('link', ''),
            'Название вакансии': vacancy.get('profession', ''),
            'Работодатель': vacancy.get('firm_name', 'не указан'),
            'Город': vacancy.get('town', {}).get('title', 'не указан'),
            'Заработная плата': vacancy.get('payment_from', 0) or vacancy.get('payment_to', 0) or 'не указана',
            'Заработная плата от': vacancy.get('payment_from', 'не указано'),
            'Заработная плата до': vacancy.get('payment_to', 'не указано'),
            'Должностные обязанности': vacancy.get('candidat', 'не указаны'),
            'Дата публикации вакансии': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d') if timestamp else 'не указано',        
            'Архивная вакансия': 'да' if vacancy.get('is_archive', False) else 'нет'
        })
    if len(vacancies_analytics) > 0:
        print(len(vacancies_analytics)),
    else:
        print(f'Ошибка: {response.status_code}, {response.text}')  

file_path = r"C:\Users\Anastasia Meteleva\Desktop\vacancies_analytics.csv"

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    fieldnames = list({key for row in vacancies_analytics for key in row.keys()})
    dict_writer = csv.DictWriter(f, fieldnames)
    dict_writer.writeheader()
    dict_writer.writerows(vacancies_analytics)

