import requests
from bs4 import BeautifulSoup
import pymongo
import time
import random
import datetime

FACIL_URL = 'http://diccionariofacil.org/diccionario/'

f = open('data/credentials.txt', 'r')
cred = f.read()

def extraction(word):
    try:
        page = requests.get(url= 'http://diccionariofacil.org/diccionario/' + word + '.html')
        soup = BeautifulSoup(page.text, 'html.parser')
        error_content = soup.find("div", {"id": "infoBoxArrowError3contendor"})
        if page.status_code == 200 and not error_content:
            definitions_content = soup.findAll(True, {"class":["definicionContent font600", "definicionContent"]})
            if len(definitions_content) > 0:
                return {
                    'result': True,
                    'data': soup
                }
            else:
                return {
                    'result': False
                }
    except:
        with open('data/logs/facil_extracion.log', 'a') as f:
            f.write(f"Error during extraction of {word} facil. Date: {datetime.datetime.utcnow()}\n")
        return {
            'result': False
        }

def transform(data):
    try:
        word = {}
        word['articles'] = []
        # Get lemma
        word['lemma'] = data.find('h3', attrs={'class': 'underlinedTitle notTextTransform'}).next_element.strip()
        # Check masculine-feminine orthopraphy
        if '-' in word['lemma']:
            # If they are not equal update lemma and adding feminine
            word['lemma'], word['feminine'] = word['lemma'].split('-')
        # Set source
        word['source'] = 'facil'
        definitions_content = data.findAll(True, {"class":["definicionContent font600", "definicionContent"]})
        if definitions_content:
            lemma_dict = {}
            lemma_dict['definitions'] = []
            for definition_content in definitions_content:
                definition = {}
                definition['order'] = int(definition_content.find('h4').text.replace('.', ''))
                span_list = definition_content.findAll('span')
                definition['definition'] = span_list[0].text
                definition['example'] = span_list[2].text
                lemma_dict['definitions'].append(definition)
            word['articles'].append(lemma_dict)

        return {
            'result': True,
            'data': word
            } 
    except:
        with open('data/logs/facil_transform.log', 'a') as f:
            f.write(f"Error during transformation of {data} facil. Date: {datetime.datetime.utcnow()}\n")
        return {
            'result': False
        }

def load(word):
    try:
        myclient = pymongo.MongoClient(cred)
        mydb = myclient["dictionary"]
        mycol = mydb['lemmasFacil']
        word['insertDate'] = datetime.datetime.utcnow()
        mycol.insert_one(word)
    except:
        with open('data/logs/facil_load.log', 'a') as f:
            f.write(f"Error during loading of {word} facil. Date: {datetime.datetime.utcnow()}\n")

def main():
    page = requests.get(url = 'http://diccionariofacil.org/diccionario/')
    soup = BeautifulSoup(page.text, 'html.parser')
    # Get all links
    selector_letra = soup.find("ul", {"class": "selectorLetra"})
    links = selector_letra.findAll("a")
    for link in links:
        # Get all entries for letters
        nextPage = link
        while(nextPage):
            page = requests.get(url = nextPage['href'])
            soup = BeautifulSoup(page.text, 'html.parser')
            if page.status_code == 200:
                entries = soup.findAll('h4')
                for entry in entries:
                    time.sleep(random.uniform(0, 0.5))
                    data_ext = extraction(entry.text)
                    if data_ext['result']:
                        data_tran = transform(data_ext['data'])
                        if data_tran['result']:
                            load(data_tran['data'])
                
                nextPage = soup.find('li', {'class': 'next'}).find('a')
                if soup.find('li', {'class': 'next'}).find('a', {'class': 'disabled'}):
                    break

    with open('data/logs/facil_process.log', 'a') as f:
            f.write(f"Crea ETL finished. Date: {datetime.datetime.utcnow()}\n")

if __name__ == "__main__":
    main()
