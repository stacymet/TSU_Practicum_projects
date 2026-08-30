import requests
import json

url = ''
TOKEN = ''

session = requests.Session()
session.headers.update({'accept': 'application/json', 'X-API-KEY': TOKEN})

result_comedies = []

response = session.get(url, params={
    'type': ['movie'],
    'genres.name': ['комедия'],
    'year': [2000],
    'sortField': ['rating.kp'],
    'selectFields': ['name', 'movieLength', 'countries'],
    'sortType': [-1],
    'page': 1,
    'limit': 250,
})

if response.status_code == 200:
    result_response = response.json()  
    result_comedies += result_response.get('docs', [])

    for page in range(2, 5):
        response = session.get(url, params={
            'type': ['movie'],
            'genres.name': ['комедия'],
            'year': [2000],
            'sortField': ['rating.kp'],
            'selectFields': ['name', 'movieLength', 'countries'],
            'sortType': [-1],
            'page': page,
            'limit': 250,
        })
        if response.status_code == 200:
            result_comedies += response.json().get('docs', [])

        if len(result_comedies) >= 1000:
            break
print(f"Записано фильмов: {len(result_comedies)}")

if result_comedies:
   with open('result_comedies_file.json', 'w', encoding='utf-8') as f:
      json.dump(result_comedies, f, ensure_ascii=False, indent=4)


