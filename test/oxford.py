import requests
import json


with open('test/oxford_credentials.json') as f:
    headers = json.load(f)

language = "es"
word_id = "tortilla"
url = "https://od-api.oxforddictionaries.com:443/api/v2/entries/" + language + "/" + word_id.lower()

r = requests.get(url, headers=headers)

print("code {}\n".format(r.status_code))
print("text \n" + r.text)
print("json \n" + json.dumps(r.json()))

