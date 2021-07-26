from os import execlpe
from typing import cast
import pymongo
import datetime

f = open('data/credentials.txt', 'r')
cred = f.read()

def extraction(data):
    try:
        return {
            'result': True, 
            'data': data
        }

    except Exception as e:
        with open('data/logs/lemario_extracion.log', 'a') as f:
            f.write(f"Error during extraction of {data}. Date: {datetime.datetime.utcnow()}\n")
        return {
            'result': False
        }

def transform(data):
    try:
        return {
            'result': True, 
            'data': data
        }

    except Exception as e:
        with open('data/logs/lemario_transform.log', 'a') as f:
            f.write(f"Error during extraction of {data}. Date: {datetime.datetime.utcnow()}\n")
        return {
            'result': False
        }

def load(data):
    try:
        myclient = pymongo.MongoClient(cred)
        mydb = myclient["dictionary"]
        mycol = mydb['lemma']
        result = mycol.find({"lemma":  data })
        if not result:
            data['date_insert'] = datetime.datetime.utcnow()
            mycol.insert_one(data)
    except:
        with open('data/logs/lemario_load.log', 'a') as f:
            f.write(f"Error during loading of {data}. Date: {datetime.datetime.utcnow()}\n")


def main():
    with open('data/lemario.txt') as reader:
        for line in reader.read().splitlines():
            data_ext = extraction(line)
            if data_ext['result']:
                data_tran = transform(data_ext['data'])
                if data_tran['result']:
                    load(data_tran['data'])

    with open('data/logs/rae_process.log', 'a') as f:
            f.write(f"Rae ETL finished. Date: {datetime.datetime.utcnow()}\n")       
        
if __name__ == "__main__":
    main()