
import requests
from bs4 import BeautifulSoup
import pymongo
uri = f'mongodb://root:de26etr28736rfsdq@localhost:27017'
connection = pymongo.MongoClient(uri)
label_collection = connection["app_db"]["label_cloud"]


URL = "https://etherscan.io/labelcloud"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}

r = requests.get(URL, headers=headers)
soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib

table = soup.find('div', attrs = {'class':'row mb-3'})
result = []
for row in table.findAll('div', attrs = {'class':'col-md-4 col-lg-3 mb-3 secondary-container'}):
    span1= row.find("span").text
    print (span1.split(" "))
    result.append({"chain": "ethereum", "label": span1.split(" ")[0]})


label_collection.insert_many(result)

for e in result:
    url = f"https://etherscan.io/tokens/label/{e['label']}"
    print (url)