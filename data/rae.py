import requests
from bs4 import BeautifulSoup
import re
import http
import time
import random
import datetime

from urllib.request import Request, urlopen
from urllib.parse import quote

RAE_URL = 'https://dle.rae.es/'
URL = 'http://163.117.129.205:80/api/lemmas'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

def extraction(word):
    try:
        word_string = quote(f'{word}')
        request = Request(url=f'{RAE_URL}{word_string}', headers=headers)
        response = urlopen(request)
        if response.code == 200:
            page = response.read()
            soup = BeautifulSoup(page, 'html.parser')
            articles = soup.findAll('article')
            if len(articles) > 0:
                return {
                    'result': True, 
                    'data': soup
                    }
            else:
                return {
                    'result': False
                }
    except Exception:
        with open('logs/crea_extracion.log', 'a') as f:
            f.write(f"Error during extraction of {word} rae. Date: {datetime.datetime.utcnow()}\n")
        return {
            'result': False
        }
        
def transform(data):
    try:
        articles = data.findAll('article')
        word = {}
        word['articles'] = []
        # Get lemma
        word['lemma'] = articles[0].find('header', attrs={'class': 'f'}).text
        # Replace numbers in lemma
        word['lemma'] = re.sub('\d', '', word['lemma']) 
        # Set source
        word['source'] = 'rae'
        # Check masculine-feminine orthopraphy
        if ',' in word['lemma']:
            splited_lemma = word['lemma'].split(', ')
            if len(splited_lemma) == 2:
                word['lemma'], word['feminine'] = splited_lemma
            else:
                # Compound noums. Example: bio-, -bio, bia 
                pass
        # Check references of the word (vease)
        if articles[0].find('p', attrs={'class': 'l2'}):
            word['references'] = articles[0].find('a', attrs={'class': 'a'}).text.replace('.','')
                    
        for article in articles:
            lemmas = article.findAll('header', attrs={'class': 'f'})
            for lemma in lemmas:
                lemma_dict = {}
                if lemma.find('i') or article.find('p', attrs={'class': 'n2'}):
                    etimology = article.find(attrs={'class': ['n2']})
                    if etimology:
                        lemma_dict['etimology'] = etimology.text
                if article.find('p', attrs={'class': 'n3'}):
                    lemma_dict['etymology'] = article.find('p', attrs={'class': 'n3'}).text
                if lemma.text.isupper():
                    lemma_dict['acronym'] = True
                if '-' in lemma.text:
                    lemma_dict['compound'] = True
                if article.find('p', attrs={'class': 'n5'}):
                    lemma_dict['orthography'] = article.find('p', attrs={'class': 'n5'}).text
                                    
                # Get list of definitions
                definitions_content = article.findAll('p', attrs={'class' : ['j', 'j1', 'j2']})
                if definitions_content:
                    # Formating entry to json model
                    lemma_dict['definitions'] = []
                    for definition_content in definitions_content:
                        definition = {}
                        definition['order'] = int(definition_content.find('span', attrs={'class': 'n_acep'}).text.replace('.', ''))
                        if definition_content.find('abbr', attrs={'class': ['d', 'g']}):
                            definition['category'] = definition_content.find('abbr', attrs={'class': ['d', 'g']})['title']
                        if definition_content.find('abbr', attrs={'class': 'c'}):
                            # TODO. Check if field is a country
                            definition['field'] = definition_content.find('abbr', attrs={'class': 'c'})['title']
                        
                        definition_content = re.findall('.*?[.]', definition_content.text)
                        definition_text = ""
                        for i in definition_content:
                            if len(i) > 8:
                                definition_text += i
                        definition['definition'] = definition_text.strip()
                        lemma_dict['definitions'].append(definition)

                # Get complex words or collocations
                complex_words = article.findAll('p', attrs={'class': ['k5', 'k6']})
                if complex_words:
                    lemma_dict['complex'] = []
                    for a in complex_words:
                        complex = {}
                        complex['forma'] = a.text
                        sibling = a.find_next_sibling('p')
                        order = sibling.find('span', attrs={'class': 'n_acep'})
                        if order:
                            complex['order'] = int(order.text.replace('.', ''))
                        category = sibling.find('abbr', attrs={'class': ['d', 'g']})
                        if category:
                            complex['category'] = category['title']            
                        if sibling.find('abbr', attrs={'class': 'c'}):
                            complex['country'] = sibling.find('abbr', attrs={'class': 'c'})['title']
                        definition_content = re.findall('.*?[.]', sibling.text)
                        definition_text = ""
                        for i in definition_content:
                            if(len(i) > 8):
                                definition_text += i
                        complex['definition'] = definition_text.strip()
                        lemma_dict['complex'].append(complex)
            
            if lemma_dict:
                word['articles'].append(lemma_dict)

        return {
            'result': True,
            'data': word
            } 
    except Exception as e:
        with open('logs/rae_transform2.log', 'a') as f:
            f.write(f"Error during transformation of {word['lemma']} rae. Date: {datetime.datetime.utcnow()}\n")
        return {
            'result': False
        }

def load(word):
    try:
        r = requests.put(f'{URL}/{word["lemma"]}', json=word)
        if r.status_code == http.HTTPStatus.CREATED:
            print(f'Lemma {word["lemma"]} created')

    except:
        with open('logs/rae_load.log', 'a') as f:
            f.write(f"Error during loading of {word} rae. Date: {datetime.datetime.utcnow()}\n")

def main():
    with open('lemario.txt') as reader:
        for line in reader.read().splitlines():
            #time.sleep(random.uniform(0, 0.5))
            data_ext = extraction(line)
            if data_ext['result']:
                data_tran = transform(data_ext['data'])
                if data_tran['result']:
                    load(data_tran['data'])

    with open('logs/rae_process.log', 'a') as f:
            f.write(f"Rae ETL finished. Date: {datetime.datetime.utcnow()}\n")       
        
if __name__ == "__main__":
    main()
