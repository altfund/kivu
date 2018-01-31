import coinmarketcap as cmc

def get_coinmarket_data(global_quote_currency='USD'):
    coinmarket_ticker_data = cmc.Market.ticker(convert = global_quote_currency)
    coinmarket_data = {x['symbol']: x for x in coinmarket_ticker_data}
    for x in coinmarket_data:
        coinmarket_data[x]['mark_price'] = coinmarket_data[x]['price_'+global_quote_currency.lower()]
    return(coinmarket_data)
    
def calculate_altfundx_weights(currencies=[], mark_prices=None, global_quote_currency="USD"):

    altfundX = copy.deepcopy(mark_prices)

    for currency in currencies:
        altfundX[currency]['allocation_percent'] = float(altfundX[currency]["market_cap_"+global_quote_currency.lower()])/sum([float(altfundX[x]["market_cap_"+global_quote_currency.lower()]) for x in altfundX if x in currencies])
        #altfundX = calculate_altfundx_allocation(currencies=altfundx_currencies, aum_usd=current_holdings_value, mark_prices=mark_prices)
        
    weights = {x: altfundX[x] for x in currencies}
    return(weights)#,'rounded_price_usd','optimal_holdings']])
#calculate_altfundx_allocation(currencies=['ETH','BTC'])

