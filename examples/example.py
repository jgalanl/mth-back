import requests

API_URL = 'http://163.117.129.205/api'

url = f'{API_URL}/lemmas/programar'
r = requests.get(url=url)

print(f'code: {r.status_code} \n')
print(f'text: {r.text} \n')
print(f'json: {r.json()}')