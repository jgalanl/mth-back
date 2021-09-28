from datetime import datetime
import http
import requests

url = 'http://localhost:80/api/lemmas'

def extraction(data):
    try:
        return {
            'result': True, 
            'data': data
        }

    except Exception as e:
        with open('logs/lemario_extracion.log', 'a') as f:
            f.write(f"Error during extraction of {data}. Exception: {e}. Date: {datetime.utcnow()}\n")
        return {
            'result': False
        }

def transform(data):
    try:
        return {
            'result': True, 
            'data': {
                'lemma': data.lower()
            }
        }

    except Exception as e:
        with open('logs/lemario_transform.log', 'a') as f:
            f.write(f"Error during extraction of {data}. Exception: {e}. Date: {datetime.utcnow()}\n")
        return {
            'result': False
        }

def load(data):
    try:
        r = requests.post(url, json=data)
        if r.status_code == http.HTTPStatus.CREATED:
            print(f'Lemma {data["lemma"]} created')

    except Exception as e:
        with open('logs/lemario_load.log', 'a') as f:
            f.write(f"Error during loading of {data}. Exception: {e}. Date: {datetime.utcnow()}\n")


def main():
    with open('lemario.txt') as reader:
        for line in reader.read().splitlines():
            data_ext = extraction(line)
            if data_ext['result']:
                data_tran = transform(data_ext['data'])
                if data_tran['result']:
                    load(data_tran['data'])

    with open('logs/lemario_process.log', 'a') as f:
            f.write(f"Rae ETL finished. Date: {datetime.utcnow()}\n")       
        
if __name__ == "__main__":
    main()