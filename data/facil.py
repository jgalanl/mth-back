import requests
from bs4 import BeautifulSoup

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
        print(f"Error during the extraction of {word} word")
        
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
        print(f"Error during the transformation of {word['lemma']} word")
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
        print(f"Error during the load of {word['lemma']} word")

def main():
    with open('data/lemario.txt') as reader:
        for line in reader.read().splitlines():
            time.sleep(random.uniform(0, 0.5))
            data_ext = extraction(line)
            if data_ext['result']:
                data_tran = transform(data_ext['data'])
                if data_tran['result']:
                    load(data_tran['data'])

    print("Finish!") 

if __name__ == "__main__":
    main()
