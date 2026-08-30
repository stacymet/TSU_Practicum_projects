import requests
import json

url = ''
api_key = ''

params = {
    'key': api_key,
    'q': 'Tomsk',

}
response = requests.get(url, params=params)

if response.status_code:
    weather = response.json()

city_name = weather['location']['name']
temp_c = weather['current']['temp_c']
feelslike_c = weather['current']['feelslike_c']

print(f'Город: {city_name}')
print(f'Температура воздуха {temp_c}°C')
print(f'Ощущается как {feelslike_c}°C')