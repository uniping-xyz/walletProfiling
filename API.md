#### TOKEN SEARCH

```
r = requests.get("http://localhost:8006/v1/api/search/tokens/text", headers={"token": token}, params={ "chain": "ethereum", "text": "uniswap"})

{'message': None,
 'count': 0,
 'data': {'erc20': [{'id': 'uniswap',
    'symbol': 'uni',
    'name': 'Uniswap',
    'ethereum': '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',
    'polygon': '0xb33eaad8d922b1083446dc23f610c2567fb5180f',
    'binance_smart_chain': '0xbf5140a22578168fd562dccf235e5d43a02ce9b1'}],
  'erc721': [{'id': '811a9bf4-1c17-5f5e-8989-81ddbd7fd499',
    'name': 'Uniswap V3 Positions',
    'logo': 'collection/811a9bf4-1c17-5f5e-8989-81ddbd7fd499/logo.png',
    'contracts': ['0xC36442b4a4522E871399CD717aBDD847Ab11FE88'],
    'verified': True,
    'token_type': 'erc721'}],
  'erc1155': []},
 'error': False,
 'success': True}
```

### Token Transfers
#### ERC721
```
r = requests.get("http://localhost:8006/v1/api/transfers/token_transfers", 
                  headers={"token": token}, 
                  params= {"chain": "ethereum", 
                          "erc_type": "ERC1155", 
                          "contract_address": "0x850d754a640f640b8d9844518f584ee131a57c9d"})

response = {"data": [{'from': '0x0000000000000000000000000000000000000000',
   'to': '0xd46eb557762ebcdce876ca57040e3caa54836054',
   'block_timestamp': '2022-11-28T11:45:35',
   'contract_address': '0x850d754a640f640b8d9844518f584ee131a57c9d',
   'token_id': 135099432,
   'quantity': 1,
   'transfer_type': 'single',
   'type': 'mint'},
  {'from': '0xd46eb557762ebcdce876ca57040e3caa54836054',
   'to': '0xb4b57125af2acf9bf605a9d9c3d256537876f65a',
   'block_timestamp': '2022-11-28T11:45:35',
   'contract_address': '0x850d754a640f640b8d9844518f584ee131a57c9d',
   'token_id': 3786168522,
   'quantity': 1,
   'transfer_type': 'single',
   'type': 'send'}],
 'error': False,
 'success': True}

```




### Most popular tokens
```
r = requests.get("http://localhost:8006/v1/api/most_popular/tokens/most_popular", 
            headers={"token": token}, 
            params={"chain": "ethereum", "erc_type": "ERC20"}

response = {'message': None,
 'count': 0,
 'data': [{'total_transactions': 347004,
   'contract_address': '0x3819f64f282bf135d62168c1e513280daf905e06',
   'name': 'Hedron',
   'symbol': 'HDRN'},
  {'total_transactions': 8095,
   'contract_address': '0x4fabb145d64652a948d72533023f6e7a623c7c53',
   'name': 'Binance USD',
   'symbol': None},
  {'total_transactions': 7728,
   'contract_address': '0x04a6b6de116fb8bf57e5ee8b05e0293ea3639fe8',
   'name': 'Proof of Memes',
   'symbol': 'ETH2.0'}],
 'error': False,
 'success': True}
```