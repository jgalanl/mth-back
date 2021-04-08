import pymongo
import datetime

f = open('data/credentials.txt', 'r')
cred = f.read()

def extraction(data):
    try: 
        data = data.split('\t')
        return {
            'result': True, 
            'data': data
            }
    except:
        with open('data/logs/crea_extracion.log', 'a') as f:
            f.write(f"Error during extraction of {data} crea. Date: {datetime.datetime.utcnow()}\n")
        return {
            'result': False
        }

def transform(data):
    try:
        word = {}
        word['lemma'] = data[1].strip()
        word['abs_freq'] = int(data[2].strip().replace(',', ''))
        word['norm_freq'] = float(data[3].strip())

        return {
            'result': True,
            'data': word
            } 
    except:
        with open('data/logs/crea_transform.log', 'a') as f:
            f.write(f"Error during transformation of {data} crea. Date: {datetime.datetime.utcnow()}\n")
        return {
            'result': False
        }

def load(word):
    try:
        myclient = pymongo.MongoClient(cred)
        mydb = myclient["frequencies"]
        mycol = mydb['crea']
        word['insert_date'] = datetime.datetime.utcnow()
        mycol.insert_one(word)
    except:
        with open('data/logs/crea_load.log', 'a') as f:
            f.write(f"Error during loading of {data} crea. Date: {datetime.datetime.utcnow()}\n")

def main():
    with open('data/crea_total.txt') as reader:
        for line in reader.read().splitlines()[1:]:
            data_ext = extraction(line)
            if data_ext['result']:
                data_tran = transform(data_ext['data'])
                if data_tran['result']:
                    load(data_tran['data'])

    with open('data/logs/crea_process.log', 'a') as f:
            f.write(f"Crea ETL finished. Date: {datetime.datetime.utcnow()}\n")


if __name__ == '__main__':
    main()     