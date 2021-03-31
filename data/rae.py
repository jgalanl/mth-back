import requests
from bs4 import BeautifulSoup
import re
import json

RAE_URL = 'https://dle.rae.es/'

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
        word['definitions'] = []
        word['compound'] = []

        # Get lemma
        word['lemma'] = articles[0].find('header', attrs={'class': 'f'}).text
                
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
                if lemma.find('i') or article.find('p', attrs={'class': 'n2'}):
                    word['etymology'] = article.find('p', attrs={'class': 'n2'}).text
                if article.find('p', attrs={'class': 'n3'}):
                    word['etymology'] = article.find('p', attrs={'class': 'n3'}).text
                if lemma.text.isupper():
                    word['acronym']: True
                if '-' in lemma.text:
                    word['compound']: True
                if article.find('p', attrs={'class': 'n5'}):
                    word['orthography'] = article.find('p', attrs={'class': 'n5'}).text
                    
                # Extraer las definiciones
                definitions_content = article.findAll('p', attrs={'class' : ['j', 'j1', 'j2']})
                if definitions_content:
                    # Para cada entrada formateamos su contenido en formato json
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
                                word['definitions'].append(definition)
                        # Extraer las formas complejas
                        for a in article.findAll('p', attrs={'class': ['k5', 'k6']}):
                            # collocations?
                            compound = {}
                            compound['forma'] = a.text
                            sibling = a.find_next_sibling('p')
                            compound['order'] = int(sibling.find('span', attrs={'class': 'n_acep'}).text.replace('.', ''))
                            compound['category'] = sibling.find('abbr', attrs={'class': ['d', 'g']})['title']
                            
                            if sibling.find('abbr', attrs={'class': 'c'}):
                                compound['country'] = sibling.find('abbr', attrs={'class': 'c'})['title']
                                definition_content = re.findall('.*?[.]', sibling.text)
                                definition_text = ""
                                for i in definition_content:
                                    if(len(i) > 8):
                                        definition_text += i
                                                            
                                compound['definition'] = definition_text.strip()
                            word['compound'].append(compound)

        return json.dumps(word, ensure_ascii=False)  
    except:
        print(f"Error during the transformation of {word} word")
        
        return {
            'result': False
        }


def load():
    pass



def main():
    # print(get_definition_rae('inteligencia'))
    response = extraction("caravana")

    if response['result']:
        data = response['data']
        t = transform(data)
        print(t)

if __name__ == "__main__":
    main()
