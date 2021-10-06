from datetime import datetime
from http import HTTPStatus
import requests

ARASAAC_URL = 'https://api.arasaac.org/api/pictograms/es/bestsearch/'
PICTO_URL = 'https://api.arasaac.org/api/pictograms/'
URL = 'http://163.117.129.205:80/api/lemmas'


def extraction(data):
    try:
        ext_req = requests.get(f'{ARASAAC_URL}{data}')
        if ext_req.status_code == HTTPStatus.OK:
            return {
                'result': True,
                'data': {
                    'lemma': data,
                    'ext_data': ext_req.json()
                }
            }
        else:
            return {
                'result': False
                }

    except Exception as e:
        with open('logs/pictos_extracion.log', 'a+') as f:
            f.write(f"Error during extraction of {data}. Exception: {e}. Date: {datetime.utcnow()}\n")
        return {
            'result': False
        }

def transform(data):
    try:
        pictos = list()
        for picto in data['ext_data']:
            pictos.append(f'{PICTO_URL}{picto["_id"]}')
        return {
            'result': True,
            'data': {
                'lemma': data['lemma'],
                'pictos': pictos
            }
        }

    except Exception as e:
        with open('logs/pictos_transform.log', 'a+') as f:
            f.write(f"Error during extraction of {data}. Exception: {e}. Date: {datetime.utcnow()}\n")
        return {
            'result': False
        }

def load(data):
    try:
        r = requests.put(f'{URL}/{data["lemma"]}', json=data)
        if r.status_code == HTTPStatus.OK:
            print(f'Lemma {data["lemma"]} created')

    except Exception as e:
        with open('logs/pictos_load.log', 'a+') as f:
            f.write(f"Error during loading of {data}. Exception: {e}. Date: {datetime.utcnow()}\n")


def main():
    try:
        with open('lemario.txt') as reader:
            for line in reader.read().splitlines():
                data_ext = extraction(line)
                if data_ext['result']:
                    data_tran = transform(data_ext['data'])
                    if data_tran['result']:
                        load(data_tran['data'])
        
        with open('logs/lemario_process.log', 'a+') as f:
                f.write(f"Rae ETL finished. Date: {datetime.utcnow()}\n")

    except Exception as e:
        print(e)       
        
if __name__ == "__main__":
    main()