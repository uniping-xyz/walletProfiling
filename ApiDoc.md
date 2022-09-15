
#### Search token

```
r = requests.get("http://localhost:8001/v1/api/find_address/search_token", params = {"token_name": "unis", "chain": "ethereum"})

{'message': None,
 'count': 0,
 'data': [{'id': 'aave-amm-unisnxweth',
   'symbol': 'aammunisnxweth',
   'name': 'Aave AMM UniSNXWETH',
   'ethereum': '0x38e491a71291cd43e8de63b7253e482622184894',
   'polygon': None,
   'binance_smart_chain': None},
  {'id': 'unisocks',
   'symbol': 'socks',
   'name': 'Unisocks',
   'ethereum': '0x23b608675a2b2fb1890d3abbd85c5775c51691d5',
   'polygon': None,
   'binance_smart_chain': None},
  {'id': 'unistake',
   'symbol': 'unistake',
   'name': 'Unistake',
   'ethereum': '0x9ed8e7c9604790f7ec589f99b94361d8aab64e5e',
   'polygon': None,
   'binance_smart_chain': None},
  {'id': 'uniswap',
   'symbol': 'uni',
   'name': 'Uniswap',
   'ethereum': '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',
   'polygon': '0xb33eaad8d922b1083446dc23f610c2567fb5180f',
   'binance_smart_chain': '0xbf5140a22578168fd562dccf235e5d43a02ce9b1'}],
 'error': False,
 'success': True}
 ```