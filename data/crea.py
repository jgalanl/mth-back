import datetime
import requests
import http

URL = 'http://163.117.129.205:80/api/lemmas'

def extraction(data):
    try: 
        data = data.split('\t')
        return {
            'result': True, 
            'data': data
            }
    except:
        with open('logs/crea_extracion.log', 'a') as f:
            f.write(f"Error during extraction of {data} crea. Date: {datetime.datetime.utcnow()}\n")
        return {
            'result': False
        }

def transform(data):
    try:
        word = {
            'lemma': data[1].strip(),
            'abs_freq': int(data[2].strip().replace(',', '')),
            'norm_freq': float(data[3].strip())
        }

        return {
            'result': True,
            'data': word
            } 
    except:
        with open('logs/crea_transform.log', 'a') as f:
            f.write(f"Error during transformation of {data} crea. Date: {datetime.datetime.utcnow()}\n")
        return {
            'result': False
        }

def load(word):
    try:
        r = requests.put(f'{URL}/{word["lemma"]}', json=word)
        if r.status_code == http.HTTPStatus.OK:
            print(f'Lemma {word["lemma"]} created')
    except:
        with open('logs/crea_load.log', 'a') as f:
            f.write(f"Error during loading of {word} crea. Date: {datetime.datetime.utcnow()}\n")

def main():
    with open('crea_total.txt') as reader:
        for line in reader.read().splitlines()[1:]:
            data_ext = extraction(line)
            if data_ext['result']:
                data_tran = transform(data_ext['data'])
                if data_tran['result']:
                    load(data_tran['data'])

    with open('logs/crea_process.log', 'a') as f:
            f.write(f"Crea ETL finished. Date: {datetime.datetime.utcnow()}\n")


if __name__ == '__main__':
    main()     
