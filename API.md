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