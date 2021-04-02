import requests
from bs4 import BeautifulSoup
import re
import json
import pymongo
import re
import time
import random
import datetime

RAE_URL = 'https://dle.rae.es/'

f = open('data/credentials.txt', 'r')
cred = f.read()

def extraction(word):
    try:    
        page = requests.get(url = RAE_URL + word)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
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
    except:
        print(f"Error during the extraction of {word} word")
        
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
        # Replace numbers in lemma TODO
        word['lemma'] = re.sub('\d', '', word['lemma']) 
        print(word['lemma'])
        # Set source
        word['source'] = 'rae'
        # Check masculine-feminine orthopraphy
        if ',' in word['lemma']:
            # If they are not equal update lemma and adding feminine
            word['lemma'], word['feminine'] = word['lemma'].split(', ')
        # Check references of the word (vease)
        if articles[0].find('p', attrs={'class': 'l2'}):
            word['references'] = articles[0].find('a', attrs={'class': 'a'}).text.replace('.','')
                    
        for article in articles:
            lemmas = article.findAll('header', attrs={'class': 'f'})
            for lemma in lemmas:
                lemma_dict = {}
                if lemma.find('i') or article.find('p', attrs={'class': 'n2'}):
                    lemma_dict['etymology'] = article.find('p', attrs={'class': 'n2'}).text
                if article.find('p', attrs={'class': 'n3'}):
                    lemma_dict['etymology'] = article.find('p', attrs={'class': 'n3'}).text
                if lemma.text.isupper():
                    lemma_dict['acronym']: True
                if '-' in lemma.text:
                    lemma_dict['compound']: True
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
                            definition['field'] = definition_content.find('abbr', attrs={'class': 'c'})['title']
                        
                        definition_content = re.findall('.*?[.]', definition_content.text)
                        definition_text = ""
                        for i in definition_content:
                            if(len(i) > 8):
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
                        complex['order'] = int(sibling.find('span', attrs={'class': 'n_acep'}).text.replace('.', ''))
                        complex['category'] = sibling.find('abbr', attrs={'class': ['d', 'g']})['title']            
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
    except:
        print(f"Error during the transformation of {word['lemma']} word")
        return {
            'result': False
        }

def load(word):
    try:
        myclient = pymongo.MongoClient(cred)
        mydb = myclient["dictionary"]
        mycol = mydb['lemmasRae']
        word['insertDate'] = datetime.datetime.utcnow()
        mycol.insert_one(word)
    except:
        print(f"Error during the load of {word['lemma']} word")

def main():
    with open('data/lemario.txt') as reader:
        for line in reader.read(5).splitlines():
            time.sleep(random.uniform(1, 5.9))
            data_ext = extraction(line)
            if data_ext['result']:
                data_tran = transform(data_ext['data'])
                if data_tran['result']:
                    load(data_tran['data'])
        
if __name__ == "__main__":
    main()
