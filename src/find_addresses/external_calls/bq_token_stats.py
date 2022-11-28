
from google.cloud import bigquery
from sanic.request import RequestParameters

"""
with transactions AS (
select *
  from `pingboxproduction.Address.total_transactions_pertoken_perday`
  where token_address = lower("0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0")
),
unique_addresses AS (
  select *
    from `pingboxproduction.Address.unique_addresses_pertoken_perday`
    where token_address = lower("0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0")
)
select transactions.m_block_timestamp as date, transactions.total_transactions, unique_addresses.unique_addresses from
 transactions
JOIN
  unique_addresses 
ON transactions.m_block_timestamp = unique_addresses.m_block_timestamp
ORDER BY
    transactions.m_block_timestamp DESC
"""
async def fetch_token_stats(app: object, request_args: RequestParameters) -> list:
    query = f"""
                with transactions AS (
                    select *
                        from `pingboxproduction.Address.total_transactions_pertoken_perday`
                        where token_address = lower("{request_args.get('token_address')}")
                    ),
                unique_addresses AS (
                    select *
                        from `pingboxproduction.Address.unique_addresses_pertoken_perday`
                        where token_address = lower("{request_args.get('token_address')}")
                    )
                
                select transactions.m_block_timestamp as date, 
                    transactions.total_transactions, 
                    unique_addresses.unique_addresses 
                from
                    transactions
                JOIN
                    unique_addresses 
                ON transactions.m_block_timestamp = unique_addresses.m_block_timestamp
                ORDER BY
                transactions.m_block_timestamp DESC
    """
    client = bigquery.Client()
    results = client.query(query)
    if results:
        result = []
        for row in results.result():
            result.append({
                    "total_transactions": row['total_transactions'],
                    "timestamp": row['date'].strftime("%s"),
                    "unique_addresses": row["unique_addresses"]
                    # "name": name,
                    # "symbol": symbol
            }) 
        return result
    return []