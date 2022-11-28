#### TOKEN SEARCH

```
url = "http://localhost:8006/v1/api/search/tokens/text"
headers={"token": token} 
params={ "chain": "ethereum", "text": "uniswap"}

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
url = "http://localhost:8006/v1/api/transfers/token_transfers" 
headers={"token": token}, 
params= {"chain": "ethereum", "erc_type": "ERC1155", "contract_address": "0x850d754a640f640b8d9844518f584ee131a57c9d"})

response = {"data": 
            [{'from': '0x0000000000000000000000000000000000000000',
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

#### ERC20
```
url = "http://localhost:8006/v1/api/transfers/token_transfers" 
headers={"token": token}
params={ "chain": "ethereum", "erc_type": "ERC20", "contract_address": "0x04a6b6de116fb8bf57e5ee8b05e0293ea3639fe8"})

response ={'message': None,
          'count': 0,
          'data': [{'block_number': 16068303,
            'block_timestamp': '2022-11-28T11:51:47',
            'block_hash': '0x46b2f49339e1d7f3cb7d5c1c74fc989a7a0a3ccd0dd1af5df29e2fc46a322e63',
            'transaction_hash': '0x9f51a8fb1994f1dfb9de690b2c71366c47b8e80ebf0dacc7c032df4fa22f8b1a',
            'log_index': 155,
            'token_address': '0x04a6b6de116fb8bf57e5ee8b05e0293ea3639fe8',
            'from_address': '0x675ed8e77f50969a0974a341e77eb1ec3fa19a29',
            'to_address': '0x51d73d48e8bc4f0e669a62a5da0e54479e239c73',
            'value': 169661096072481604668515279},
            {'block_number': 16068303,
            'block_timestamp': '2022-11-28T11:51:47',
            'block_hash': '0x46b2f49339e1d7f3cb7d5c1c74fc989a7a0a3ccd0dd1af5df29e2fc46a322e63',
            'transaction_hash': '0x9f51a8fb1994f1dfb9de690b2c71366c47b8e80ebf0dacc7c032df4fa22f8b1a',
            'log_index': 159,
            'token_address': '0x04a6b6de116fb8bf57e5ee8b05e0293ea3639fe8',
            'from_address': '0x51d73d48e8bc4f0e669a62a5da0e54479e239c73',
            'to_address': '0x04a6b6de116fb8bf57e5ee8b05e0293ea3639fe8',
            'value': 13572887685798528373481222}],
          'error': False,
          'success': True}

```




### Most popular tokens
```
url = "http://localhost:8006/v1/api/most_popular/tokens/most_popular"
headers={"token": token}
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


### Wallet Stats 

#### NFT Balances of a wallet address
```
url = "http://localhost:8006/v1/api/wallet/nft_balances"
headers={"token": token}
params={ "chain": "ethereum", "wallet_address": "0x3213eF068D8Def86A068D0cbBcbb3c00664894Ad"}

response =  {'message': None,
            'count': 0,
            'data': {'result': [{'id': 'eaf08070-9c80-5836-9ab1-84d1552019fc',
                'token_id': '115587061795188303249084852614891348655679814947926012441049663984924904888601',
                'image_url': 'token/0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85/eaf08070-9c80-5836-9ab1-84d1552019fc.svg',
                'name': 'uniping.eth',
                'contract_address': '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85',
                'wallets': [],
                'burned': False,
                'contract_name': 'ENS: Ethereum Name Service'},
              {'id': '2e3f315c-eb45-573d-bc27-3d3dc83a3859',
                'token_id': '15800883863004751456966042702890727823095680308013222743739981157277262473414',
                'image_url': '',
                'name': '#15800883863004751456966042702890727823095680308013222743739981157277262473414',
                'contract_address': '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85',
                'wallets': [],
                'burned': False,
                'contract_name': 'ENS: Ethereum Name Service'}],
              'next_page_token': ''},
            'error': False,
            'success': True}
```
#### ERC20 Token Balances of a wallet address
```
url = "http://localhost:8006/v1/api/wallet/erc20_balances" 
headers={"token": token} 
params={ "chain": "ethereum", "wallet_address": "0x3213eF068D8Def86A068D0cbBcbb3c00664894Ad"}
response = {'message': None,
          'count': 0,
          'data': [{'contract_address': '0x09a3ecafa817268f77be1283176b946c4ff2e608',
            'contract_name': {'contracts': '0x09a3EcAFa817268f77BE1283176B946C4ff2E608',
              'id': 'mirror-protocol',
              'symbol': 'mir',
              'name': 'Mirror Protocol',
              'token_type': 'erc20'},
            'balance': 220.037},
            {'contract_address': '0x0f5d2fb29fb7d3cfee444a200298f468908cc942',
            'contract_name': {'contracts': '0x0F5D2fB29fb7d3CFeE444a200298f468908cC942',
              'id': 'decentraland',
              'symbol': 'mana',
              'name': 'Decentraland',
              'token_type': 'erc20'},
            'balance': 307.4},
            {'contract_address': '0x249e38ea4102d0cf8264d3701f1a0e39c4f2dc3b',
            'contract_name': {'contracts': '0x249e38Ea4102D0cf8264d3701f1a0E39C4f2DC3B',
              'id': 'ufo-gaming',
              'symbol': 'ufo',
              'name': 'UFO Gaming',
              'token_type': 'erc20'},
            'balance': 4962198.418}],
          'error': False,
          'success': True}
```


#### Wallet transactions made by wallet on a per day basis
```
url = "http://localhost:8006/v1/api/wallet/txs_per_day"
headers={"token": token}
params={ "chain": "ethereum", "wallet_address": "0x3213eF068D8Def86A068D0cbBcbb3c00664894Ad"}

response = {'message': None,
          'count': 0,
          'data': [{'tithi': '2022-08-05', 'tx_count': 1, 'eth_spent': 0.0},
            {'tithi': '2022-08-09', 'tx_count': 1, 'eth_spent': 0.0},
            {'tithi': '2022-08-13', 'tx_count': 2, 'eth_spent': 0.0},
            {'tithi': '2022-08-15', 'tx_count': 1, 'eth_spent': 0.15128282},
            {'tithi': '2022-08-19', 'tx_count': 1, 'eth_spent': 0.46849059363282447},
            {'tithi': '2022-09-26', 'tx_count': 2, 'eth_spent': 0.008393043243684443},
            {'tithi': '2022-10-20', 'tx_count': 6, 'eth_spent': 0.13},
            {'tithi': '2022-10-28', 'tx_count': 1, 'eth_spent': 0.0},
            {'tithi': '2022-11-09', 'tx_count': 1, 'eth_spent': 0.0},
            {'tithi': '2022-11-11', 'tx_count': 3, 'eth_spent': 0.11401332},
            {'tithi': '2022-11-13', 'tx_count': 1, 'eth_spent': 0.0}],
          'error': False,
          'success': True}
 ```
#### Wallet transactions made by wallet in native form
```
url = "http://localhost:8006/v1/api/wallet/txs" 
headers={"token": token} 
params={ "chain": "ethereum", "wallet_address": "0xbdfa4f4492dd7b7cf211209c4791af8d52bf5c50"})
response = {'message': None,
          'count': 0,
          'data': [{'block_timestamp': '2022-09-29T01:42:59',
            'from_address': '0xbdfa4f4492dd7b7cf211209c4791af8d52bf5c50',
            'to_address': '0x623b83755a39b12161a63748f3f595a530917ab2',
            'value_eth': 0.0,
            'transaction_fee_eth': 0.007677539509307707},
            {'block_timestamp': '2022-09-29T01:44:47',
            'from_address': '0xbdfa4f4492dd7b7cf211209c4791af8d52bf5c50',
            'to_address': '0xdef1c0ded9bec7f1a1670819833240f027b25eff',
            'value_eth': 0.0,
            'transaction_fee_eth': 0.0023241471257546076},
            {'block_timestamp': '2022-09-29T01:45:11',
            'from_address': '0xbdfa4f4492dd7b7cf211209c4791af8d52bf5c50',
            'to_address': '0xdef1c0ded9bec7f1a1670819833240f027b25eff',
            'value_eth': 0.0,
            'transaction_fee_eth': 0.0035349525699421218},
            {'block_timestamp': '2022-09-29T01:47:47',
            'from_address': '0xbdfa4f4492dd7b7cf211209c4791af8d52bf5c50',
            'to_address': '0xdef1c0ded9bec7f1a1670819833240f027b25eff',
            'value_eth': 0.0,
            'transaction_fee_eth': 0.003771319383526536},
            ...],
        'error': False,
        'success': True}
```