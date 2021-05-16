import requests
import json

headers = {
    "app_id": "45be6888",
    "app_key": "fc28e3b2831f4e5fd7858ffd7dcac97a" 
}

# app_id = "45be6888"
# app_key = "fc28e3b2831f4e5fd7858ffd7dcac97a"

language = "es"
word_id = "tortilla"
url = "https://od-api.oxforddictionaries.com:443/api/v2/entries/" + language + "/" + word_id.lower()

r = requests.get(url, headers=headers)

print("code {}\n".format(r.status_code))
print("text \n" + r.text)
print("json \n" + json.dumps(r.json()))

