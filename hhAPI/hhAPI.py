import requests
import time
import csv

URL_AREAS = ''
URL_EMPLOYERS = ''

altai_krai_ids = []

response = requests.get(URL_AREAS)
if response.status_code == 200:
    response_data = response.json()

    obj_russia = next(country for country in response_data if country['name'] == 'Россия')
    
    obj_altai_krai = next(region for region in obj_russia['areas'] if region['name'] == 'Алтайский край')

    altai_krai_ids = [area['id'] for area in obj_altai_krai['areas']]

else:
    print("Ошибка при запросе данных:", response.status_code)

all_employers = []
max_employers = 1000  

if altai_krai_ids:
    for altai_krai_id in altai_krai_ids:
        page = 0
        while len(all_employers) < max_employers:
            response_emp = requests.get(
                URL_EMPLOYERS,
                params={
                    'area': altai_krai_id,
                    'only_with_vacancies': True,
                    'sort_by': 'by_vacancies_open',  
                    'page': page,
                    'per_page': 100,
                    'locale': 'RU'
                }
            )

            if response_emp.status_code == 200:
                items = response_emp.json().get('items', [])
                
                if not items:
                    break

                for employer in items:
                    all_employers.append({
                        'id': employer['id'],
                        'name': employer['name'],
                        'vacancies_count': employer['open_vacancies'],
                        'vacancies_url': employer['vacancies_url']
                    })

                    if len(all_employers) >= max_employers:
                        break  

                page += 1
                time.sleep(0.3)

            else:
                print(f"Ошибка при запросе работодателей для региона {altai_krai_id}: {response_emp.status_code}")
                print("Ответ сервера:", response_emp.text)
                break

all_employers = sorted(all_employers, key=lambda x: x['vacancies_count'], reverse=True)


file_path = r"C:\Users\Anastasia Meteleva\Desktop\altai_krai_employers.csv"

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    fieldnames = list({key for row in all_employers for key in row.keys()})
    dict_writer = csv.DictWriter(f, fieldnames)
    dict_writer.writeheader()
    dict_writer.writerows(all_employers)



    
    

        



