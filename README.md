




## Contract page for NFT contracts

#### Stats APIS

#### NFT_sales : this is to show if this NFT has been traded on any popular decentralized exchange
```
r = requests.get("http://localhost:8006/v1/api/token/ethereum/nft_sales", 
  params={"token_address": "0x6339e5E072086621540D0362C4e3Cea0d643E114"})
```

#### Token Holders
```
r = requests.get("http://localhost:8006/v1/api/holders/ethereum/tokens", 
      params={"erc_type": "ERC721", 
        "contract_address": "0xffc6dbff68a8e92a7984e474f7b7a9856945e0fb", 
        "limit": 20})
```