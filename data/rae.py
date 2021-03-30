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
        word['complex'] = []

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
                        definition['aceptacion'] = int(definition_content.find('span', attrs={'class': 'n_acep'}).text.replace('.', ''))
                        if definition_content.find('abbr', attrs={'class': ['d', 'g']}):
                            definition['categoria'] = definition_content.find('abbr', attrs={'class': ['d', 'g']})['title']
                        if definition_content.find('abbr', attrs={'class': 'c'}):
                            definition['campo'] = definition_content.find('abbr', attrs={'class': 'c'})['title']
                        
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
                            complex_word = {}
                            complex_word['forma'] = a.text
                            sibling = a.find_next_sibling('p')
                            complex_word['aceptacion'] = int(sibling.find('span', attrs={'class': 'n_acep'}).text.replace('.', ''))
                            complex_word['categoria'] = sibling.find('abbr', attrs={'class': ['d', 'g']})['title']
                            
                            if sibling.find('abbr', attrs={'class': 'c'}):
                                complex_word['pais'] = sibling.find('abbr', attrs={'class': 'c'})['title']
                                definition_content = re.findall('.*?[.]', sibling.text)
                                definition_text = ""
                                for i in definition_content:
                                    if(len(i) > 8):
                                        definition_text += i
                                                            
                                complex_word['definition'] = definition_text.strip()
                            word['complex'].append(complex_word)

        return json.dumps(word, ensure_ascii=False)  
    except:
        print(f"Error during the transformation of {word} word")
        
        return {
            'result': False
        }


def load():
    pass


def get_definition_rae(word):
    # if request.method == 'GET':
    #     word = escape(request.args.get('word'))
        # definition_list = list()
        page = requests.get(url= 'https://dle.rae.es/' + word)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            
            
            articles = soup.findAll('article')
            palabra = {}
            palabra['definiciones'] = []
            palabra['complejas'] = []

            try:

                # Obtener el lema
                palabra['lema'] = articles[0].find('header', attrs={'class': 'f'}).text
                
                # Especificar la fuente
                palabra['fuente'] = 'rae'

                # Comprobar si hay diferencia entre el masculino y el femenino
                if ',' in palabra['lema']:
                    # Si hay diferencia actualizamos el lema e incluimos el femenino
                    palabra['lema'], palabra['femenino'] = palabra['lema'].split(', ')

                # Comprobar si la entrada tiene una referencia a otra palabra (vease)
                if articles[0].find('p', attrs={'class': 'l2'}):
                    palabra['vease'] = articles[0].find('a', attrs={'class': 'a'}).text.replace('.','')
                    
                for article in articles:
                    lemas = article.findAll('header', attrs={'class': 'f'})
                    for lema in lemas:
                        if lema.find('i') or article.find('p', attrs={'class': 'n2'}):
                            palabra['etimologia'] = article.find('p', attrs={'class': 'n2'}).text
                        
                        if article.find('p', attrs={'class': 'n3'}):
                            palabra['etimologia'] = article.find('p', attrs={'class': 'n3'}).text


                        if lema.text.isupper():
                            palabra['siglas']: True
                        
                        if '-' in lema.text:
                            palabra['compositivo']: True

                        if article.find('p', attrs={'class': 'n5'}):
                            palabra['ortografia'] = article.find('p', attrs={'class': 'n5'}).text

                        # Extraer las definiciones
                        definitions_content = article.findAll('p', attrs={'class' : ['j', 'j1', 'j2']})
                        if definitions_content:
                            # Para cada entrada formateamos su contenido en formato json
                            for definition_content in definitions_content:
                                definition = {}
                                definition['aceptacion'] = int(definition_content.find('span', attrs={'class': 'n_acep'}).text.replace('.', ''))

                                if definition_content.find('abbr', attrs={'class': ['d', 'g']}):
                                    definition['categoria'] = definition_content.find('abbr', attrs={'class': ['d', 'g']})['title']
                                if definition_content.find('abbr', attrs={'class': 'c'}):
                                    definition['campo'] = definition_content.find('abbr', attrs={'class': 'c'})['title']

                                definition_content = re.findall('.*?[.]', definition_content.text)
                                definition_text = ""
                                for i in definition_content:
                                    if(len(i) > 8):
                                        definition_text += i


                                definition['definicion'] = definition_text.strip()
                                palabra['definiciones'].append(definition)

                            # Extraer las formas complejas
                            for a in article.findAll('p', attrs={'class': ['k5', 'k6']}):
                                forma_compleja = {}
                                forma_compleja['forma'] = a.text
                                sibling = a.find_next_sibling('p')

                                forma_compleja['aceptacion'] = int(sibling.find('span', attrs={'class': 'n_acep'}).text.replace('.', ''))
                                forma_compleja['categoria'] = sibling.find('abbr', attrs={'class': ['d', 'g']})['title']

                                if sibling.find('abbr', attrs={'class': 'c'}):
                                    forma_compleja['pais'] = sibling.find('abbr', attrs={'class': 'c'})['title']

                                definition_content = re.findall('.*?[.]', sibling.text)
                                definition_text = ""
                                for i in definition_content:
                                    if(len(i) > 8):
                                        definition_text += i
                                                            
                                forma_compleja['definicion'] = definition_text.strip()
                                palabra['complejas'].append(forma_compleja)

                return json.dumps(palabra, ensure_ascii=False)  
            except:
                print("Se ha producido un error para la entrada {}".format(word))

        else:
            print("Error de conexión")

def main():
    # print(get_definition_rae('inteligencia'))
    response = extraction("caravana")

    if response['result']:
        data = response['data']
        t = transform(data)
        print(t)

if __name__ == "__main__":
    main()
