import pymongo

f = open('data/credentials.txt', 'r')
cred = f.read()

# Check extraction-load words

missed_words = list()

with open('data/lemario.txt') as reader, open('data/missed_words.txt', 'a') as f:
        for word in reader.read().splitlines():
            myclient = pymongo.MongoClient(cred)
            mydb = myclient["dictionary"]
            mycol = mydb['lemmasRae']
            result = mycol.find_one({'lemma': word},{ "_id": 0, "lemma": 1 })
            if not result:
                f.write(f'{word}\n')

print('Finish!')