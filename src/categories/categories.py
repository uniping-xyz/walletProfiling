from socket import timeout
from weakref import proxy
from xml.dom.minidom import Document
import json
import requests
from loguru import logger
from sanic import Blueprint
from bs4 import BeautifulSoup
import pandas as pd
from utils.utils import Response
from utils.errors import CustomError
import re
import aiohttp
from pymongo.errors import BulkWriteError
from pymongo import InsertOne
import time
import random
from collections import Counter
from fake_useragent import UserAgent
ua = UserAgent()


CATEGORIES_BP = Blueprint("categories", url_prefix='/categories', version=1)

#@is_subscribed()
async def category_tokens(request):
    if not request.args.get("category"):
        raise CustomError("category is required")


    match = re.findall("\(.*?\)", request.args.get("category"))
    if match:
        category = request.args.get("category").replace(match[0], "")
    else:
        category = request.args.get("category").replace(" ", "-").lower()



    base_url = f"https://www.coingecko.com/en/categories/{category}"
    for i in range(1, 4):
        params = {"page": i}
        response = requests.get(base_url, params = params)
        soup = BeautifulSoup(response.content, "html.parser")
        break

    data = pd.read_html(str(soup))
    result = data[0][["Coin", "Price", "1h", "24h", '7d', '24h Volume',  'Mkt Cap']]
    headers = ["Coin", "Price", "1h", "24h", '7d', '24h Volume',  'Mkt Cap']
    res = list( zip(result["Coin"], result["Price"], result["1h"], result["24h"], result["7d"], result['24h Volume'], result['Mkt Cap']))
    return Response.success_response(data={"data": res, "headers": headers})


@CATEGORIES_BP.get('top_categories')
async def top_categories(request):
    categories = []
    async for post in request.app.config.COINGECKO_ETH_ERC20_TOKENS.find():
        categories.extend(post.get("categories"))

    c = Counter(categories)


    # base_url = "https://www.coingecko.com/en/categories"
    # for i in range(1, 4):
    #     params = {"page": i}
    #     response = requests.get(base_url, params = params)
    #     soup = BeautifulSoup(response.content, "html.parser")
    #     break

    # data = pd.read_html(str(soup))
    # result = data[0][["Category", "1h", "24h", 'Market Capitalization']]
    # res = list( zip(result["Category"], result["1h"], result["24h"], result['Market Capitalization']))
    # headers = ["Category", "1h", "24h", 'Market Capitalization']
    return Response.success_response(data=c.most_common(100))

@CATEGORIES_BP.get('category/tokens')
#@is_subscribed()
async def category_tokens(request):
    if not request.args.get("category"):
        raise CustomError("category not suported")

    projection={"_id": False, "name": True, "ethereum_address": True, "symbol": True}
    result = []
    async for post in  request.app.config.COINGECKO_ETH_ERC20_TOKENS.find({
                        "categories": 
                            {"$in": 
                                [request.args.get("category")]}},
                                projection=projection):
        result.append(post)
    return Response.success_response(data=result)

def get_proxy_list():
    response = requests.get("https://sslproxies.org/")
    soup = BeautifulSoup(response.content, 'html5lib')
    proxies = pd.read_html(str(soup))[0]
    proxies["full"] = proxies["IP Address"] + ":" + proxies["Port"].astype(str)
    return proxies["full"].values.tolist()

async def get_one_page_coingecko(url, page_number):
    # response = requests.get(url, params = params)
    # soup = BeautifulSoup(response.content, "html.parser")
    # data = pd.read_html(str(soup), extract_links="all")
    # # return data[0]
    # proxies = get_proxy_list()

    headers = {'User-Agent': ua.random} 
    
    params = {"page": page_number}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers, timeout=30) as response:
            data =  await response.text()

    soup = BeautifulSoup(data, "html.parser")
    data = pd.read_html(str(soup), extract_links="all")
    return data[0]

async def store(request, token_list):
    _list = [InsertOne(e) for e in token_list]
    try:
        await request.app.config.COINGECKO_ETH_ERC20_TOKENS.bulk_write(_list, ordered=False)
    except BulkWriteError as bwe:
        pass


async def eth_get_all_coins(request):

    eth_url = "https://www.coingecko.com/en/categories/"
    for i in range(37, 100):
        page_number = i
        try:
            df = await get_one_page_coingecko(eth_url, page_number)
        except Exception as e:
            logger.error(e)
            break
        tokens = df.iloc[:,[2]].values.tolist()
        final_list = []
        for e in tokens:
            full = e[0][0].split(" ")
            symbol = full[-1]
            name = " ".join(full[0: -1])
            print (f"Name = <{name}>, SYMBOL = <{symbol}>")
            final_list.append({"name": name, "symbol": symbol,  "url": e[0][1]})
        await store(request, final_list)
        logger.info(f"{page_number} has been scraped")
        # time.sleep(60)
    return final_list

@CATEGORIES_BP.get('populate_eth_tokens')
async def populate_eth_tokens(request):
    await eth_get_all_coins(request)
    return Response.success_response(data={})



def get_token_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    result = soup.find_all(attrs={"class":"dropdown-item tw-text-sm tw-pl-4 tw-py-2"})
    categories = []
    chains = []
    for i in result:
        text = i.text
        link = i["href"]
        if "categories" in link.split("/"):
            categories.append(text)
        else:
            chains.append((text, link.split("/")[-1]))
    return (categories, chains)

def dump_collection():
    jsonpath = "coingecko_eth_erc20_tokens.json"
    collection = copy_coingecko_eth_erc20_tokens
    from bson.json_util import dumps
    with open(jsonpath, 'wb') as jsonfile:
        jsonfile.write(dumps(copy_coingecko_eth_erc20_tokens.find(projection={"_id": False})).encode())