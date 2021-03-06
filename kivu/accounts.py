from collections import defaultdict
import numpy as np
import copy
import time

import logging
logger = logging.getLogger('local')

from .exchanges import *

def calc_mark_price(base_currency, quote_currency, markets):
    trade_path = find_trade_path(sell_currency=base_currency,
                                buy_currency=quote_currency, 
                                markets=markets)
    trade_prices = [markets[x['market']]['price']**(-1 if x['side']=='ASK' else 1) for x in trade_path]
    mark_price = np.prod(trade_prices)**-1
    
    return mark_price
    
def calc_mark_prices(markets, global_quote_currency=None):
    currencies = list(set([y['quote_currency'] for x,y in markets.items()]+[y['base_currency'] for x,y in markets.items()]))
    mark_prices = {x:calc_mark_price(x,global_quote_currency,markets) for x in currencies}
    return(mark_prices)

def percentage_rebalance(exchange, current_holdings, weights, mark_prices, global_quote_currency="USD",tolerance_percent=0.01):
    try:
        current_holdings_value = holdings_value(holdings=current_holdings, global_quote_currency=global_quote_currency,mark_prices=mark_prices)
        print("portfolio value: ",current_holdings_value,global_quote_currency)

        optimal_holdings = unpercentagize(holdings=current_holdings,
        percents=weights,
        mark_prices=mark_prices,
        global_quote_currency=global_quote_currency)

        optimal_holdings_value = holdings_value(holdings=optimal_holdings, global_quote_currency=global_quote_currency
                                                        ,mark_prices=mark_prices)

        print(optimal_holdings_value)
        print(current_holdings_value)
        if optimal_holdings_value == current_holdings_value:
            print("Allocation function assigns optimal values consistent with current holdings value")
        else:
            print("Allocation inconsistent with current holdings value")

        # need to get this to include the intersection of the current_holdings & optimal_holdings sets
        holdings_diff = {x: (float(optimal_holdings[x]) if x in optimal_holdings else 0) - (float(current_holdings[x]) if x in current_holdings else 0) for x in list(set(list(optimal_holdings.keys())+list(current_holdings.keys())))}
        print("current: ",current_holdings)
        print("optimal: ",optimal_holdings)
        print("diffs: ",holdings_diff)

        current_percent = percentagize(holdings=current_holdings, mark_prices=mark_prices, global_quote_currency=global_quote_currency)
        total_current_percent = sum(list(current_percent.values()))
        optimal_percent = percentagize(holdings=optimal_holdings, mark_prices=mark_prices, global_quote_currency=global_quote_currency)
        total_optimal_percent = sum(list(optimal_percent.values()))

        if total_optimal_percent == total_current_percent:
            print("Allocation function assigns consistent percentage weights")
        else:
            print("Allocation percentage weights are inconsistent")
            print("Current: ",total_current_percent)
            print("Optimal: ",total_optimal_percent)

        percent_diffs = calc_holdings_diff(current_percent, optimal_percent)
        print("current: ",current_percent)
        print("optimal: ",optimal_percent)
        print("diffs: ",percent_diffs)

        total_diffs_percent = sum(list(percent_diffs.values()))
        if total_diffs_percent == 0:

            print("Percentage diffs are consistent")
        else:
            print("Percentage diffs are impossible")
            print(total_diffs_percent)

        #percent_diffs = scale_holdings_diff(percent_diffs)
        percent_diffs = filter_within_tolerance(percent_diffs, tolerance_percent=tolerance_percent)

        trades_to_make = diffs_to_trades(percent_diffs)
        print(trades_to_make)
        #diffs_to_trades(percent_diffs={"A":.5,"B":-.25,"C":-.25})


        #exchange_markets = {"BTC/USD":{'quote_currency':'USD','base_currency':'BTC'}, "ETH/USD":{'quote_currency':'USD','base_currency':'ETH'},
        #                   "LTC/USD":{'quote_currency':'USD','base_currency':'LTC'}, "ETH/BTC":{'quote_currency':'BTC','base_currency':'ETH'}}
        #exchange_paths = {}
        #find_shortest_path(graph=path_from_markets(exchange_markets), start="USD", end="ETH", path=[])
        #print(get_market_from_currencies(sell_currency="USD",buy_currency="ETH",markets=exchange_markets))
        orders = trades_to_orders(percent_transfers_to_make=trades_to_make, holdings=current_holdings,mark_prices=mark_prices
                         ,markets=exchange['markets'],global_quote_currency=global_quote_currency)
        return(orders)
    except:
        #client.captureException()
        logger.error('Error thrown in percentage_rebalance', exc_info=True)

def holdings_global_quote(holdings={}, global_quote_currency="USD",mark_prices=None):
    # returns holdings in terms of global_quote for each asset
    quoted_holdings = copy.deepcopy(holdings)

    for currency in holdings:
        #mark_price = float(mark_prices[currency]['mark_price']) if currency != global_quote_currency else 1
        mark_price = 0
        if currency in mark_prices:
            mark_price = float(mark_prices[currency])# if currency != global_quote_currency else 1
        """
        mark_price = 0
        if currency == global_quote_currency:
            mark_price = 1
        elif currency not in list(mark_prices.keys()):
            mark_price = 0
        else:
            mark_price = float(mark_prices[currency]['mark_price'])
        """
        #print(type(holdings[currency]))
        #print(type(mark_price))
        #if currency != global_quote_currency:
        quoted_holdings[currency] = float(holdings[currency]) * mark_price

    return(quoted_holdings)
    
def holdings_value(holdings={}, global_quote_currency="USD",mark_prices=None):
    try:
        # Calculate the total market value of a holdings dict given curent market pricing
        quoted_holdings = holdings_global_quote(holdings, global_quote_currency,mark_prices)
        marked_portfolio_value = sum([quoted_holdings[x] for x in quoted_holdings])
    except:
        #client.captureException()
        logger.error('Error thrown in holdings value', exc_info=True)
    return(marked_portfolio_value)
    
def percentagize(holdings, mark_prices, global_quote_currency='USD'):
    #x_percents = {x: Fraction(holdings[x], holdings_value(current_holdings=holdings, global_quote_currency="USD"
    #                                            ,current_pricing="coinmarketcap_tickerdump.csv")) for x in holdings}
    # Value of currency X in terms of global_quote / Total value of portfolio in terms of global_quote
    # TODO: check that holdings.keys() and mark_prices.keys() overlap (we have a mark price for every holding)
    x_percemts = {}
    try:
        x_percents = {x: (float(holdings[x]) *
                         (float(mark_prices[x])
                         if x != global_quote_currency else 1))
                          /holdings_value(holdings=holdings, global_quote_currency=global_quote_currency
                                                    ,mark_prices=mark_prices)
                      for x in holdings if x in mark_prices}

        #x_percents =
    except:
        #client.captureException()
        logger.error('Error thrown in percentagize', exc_info=True)
    return(x_percents)

def unpercentagize(holdings, percents, mark_prices, global_quote_currency="USD"):

    try:
        #make sure that percents equal 100
        # filter out none values for non crypto currencies
        percents = {x: percents[x] if percents[x] is not None else 0 for x in percents }
        print(percents)
        total_percent = sum([percents[x] for x in percents])
        percents = {x: percents[x]/total_percent for x in percents}

        optimal_holdings = {x:0 for x in list(set(list(holdings.keys())+list(percents.keys())))}
        aum_quote = holdings_value(holdings, global_quote_currency, mark_prices)
        for currency in optimal_holdings:
            print("loop in optimal holdings")
            try:
                weight = 0 if currency not in list(percents.keys()) else percents[currency]
                mark_price = 1 if currency==global_quote_currency else float(mark_prices[currency])
                if mark_price != 0:
                    optimal_holdings[currency] = (float(aum_quote) * float(weight))/float(mark_price)
            except:
                #client.captureException()
                logger.info('Error encountered when processing %s in optimal holdings', currency)
                logger.error('Error thrown in unpercentagize loop', exc_info=True)
    except:
        #client.captureException()
        logger.error('Error thrown in unpercentagize', exc_info=True)

    return(optimal_holdings)


def calc_holdings_diff(current_holdings, optimal_holdings):
    return({x: (float(optimal_holdings[x]) if x in optimal_holdings else 0) -
            (float(current_holdings[x]) if x in current_holdings else 0)
            for x in list(set(list(optimal_holdings.keys())+list(current_holdings.keys())))})


def filter_percent_position_change_tolerance(percent_diffs, current_percent, tolerance=0.01):
    pass


def scale_holdings_diff(percent_diffs, scaling_factor=.99):
    scaled_diffs = {x: percent_diffs[x]*scaling_factor for x in percent_diffs}
    return(scaled_diffs)

def filter_within_tolerance(percent_diffs, tolerance_percent=.01):
    filtered_diffs = None
    try:
        filtered_diffs = {x: percent_diffs[x] for x in percent_diffs if abs(percent_diffs[x])>tolerance_percent}
    except:
        #client.captureException()
        logger.error('Error thrown in filter_within_tolerance', exc_info=True)
    return(filtered_diffs)

def diffs_to_trades(percent_diffs):
    try:
        #Inputs:
        #Dict of Symbols
            # market_price_global_quote: Value of assets in terms of global_quote_currency
            # current_holdings: how much of the asset we hold
            # optimal_percentage_allocation: what percentage of our wealth we should hold in this currency

        #Results:
            #Trades to Make
                #Buy Currency
                #Sell Currency
                #Amount
                #Price


        print(percent_diffs)
        neg_diffs = {x:percent_diffs[x] for x in percent_diffs if percent_diffs[x]<0}
        pos_diffs = {x:percent_diffs[x] for x in percent_diffs if percent_diffs[x]>0}
        temp_diffs = copy.deepcopy(percent_diffs)
        portfolio_turnover = 0
        percent_transfers_to_make = []
        for sell_currency in neg_diffs:
            for buy_currency in pos_diffs:
                txn_percent = min(abs(temp_diffs[sell_currency]),temp_diffs[buy_currency])
                percent_transfers_to_make.append({"sell_currency":sell_currency,
                                                 "buy_currency":buy_currency,
                                                 "trade_percent":txn_percent})
                temp_diffs[buy_currency]-=txn_percent
                temp_diffs[sell_currency]+=txn_percent
                portfolio_turnover += txn_percent
                print("Trade",txn_percent*100,"% of portfolio value from",sell_currency,"to",buy_currency)

        sum_of_diffs = sum([abs(percent_diffs[x]) for x in percent_diffs])
        if 2*portfolio_turnover==sum_of_diffs:
            print("Portfolio turnover equals sum of neg-diffs")
        else:
            print("Portfolio turnover inconsistent")
            print(2*portfolio_turnover)
            print(sum_of_diffs)

        print(percent_diffs)
        return(percent_transfers_to_make)
    except:
        #client.captureException()
        logger.error('Error thrown in diffs_to_trades', exc_info=True)

def find_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not start in graph:
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath: return newpath
    return None

def find_shortest_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not start in graph:
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest

def path_from_markets(exchange_markets):
    exchange_paths = defaultdict(list)
    for em in exchange_markets:
        flip_dict = {1:'base',-1:'quote'}
        for flop in flip_dict:
            from_currency = exchange_markets[em][flip_dict[flop]+'_currency']
            to_currency = exchange_markets[em][flip_dict[-1*flop]+'_currency']
            exchange_paths[from_currency].append(to_currency)
    #print(dict(exchange_paths))
    return(dict(exchange_paths))


def get_market_from_currencies(sell_currency, buy_currency, markets):
    currencies_list = [sell_currency, buy_currency]
    possible_markets = [x for x in markets if (set([markets[x]["quote_currency"],markets[x]["base_currency"]]) == set(currencies_list))]
    #print(possible_markets)
    return(possible_markets)

def find_trade_path(sell_currency, buy_currency, markets):
    # Output
    # list of dicts:
    # Trade 0.19528722442408997 % of portfolio value from BTC to LTC
    #
    # [{market:, side}]
    path = find_shortest_path(graph=path_from_markets(markets),start=sell_currency,end=buy_currency)
    #print(path_from_markets(markets))
    synthetic_market = []
    if path:
        for step in range(0,len(path)-1):
            #print("Sell",path[step],"Buy",path[step+1])
            #print(path[step+1])
            single_market = get_market_from_currencies(path[step], path[step+1], markets=markets)[0]

            side = "BID" if markets[single_market]['quote_currency']==path[step] else "ASK"
            synthetic_market += [{'market': single_market,'side': side}]
    return(synthetic_market)


#import itertools
#currencies = ["BTC","ETH","LTC","USD"]
#for pair in list(itertools.permutations(currencies,2)):
#    print(pair)
#    print("Sell",pair[0],"Buy",pair[1])
#    print("Market", find_trade_path(sell_currency=pair[0],buy_currency=pair[1],markets=exchange_markets))

#print(create_synthetic_market(sell_currency="USD",buy_currency="ETH",markets=exchange_markets))


def trades_to_orders(percent_transfers_to_make, holdings, mark_prices, global_quote_currency, markets):
    try:
        #Inputs:
            #Trades to make
        #Results
            #orders_to_make: list of lists of dicts
        account_value = holdings_value(holdings, global_quote_currency=global_quote_currency,mark_prices=mark_prices)
        orders = []
        for trade in percent_transfers_to_make:
            try:
                trade_path = find_trade_path(trade['sell_currency'], trade['buy_currency'], markets) # find market with between sell_currency & buy_currency
                print(trade_path)

                temp_orders = []
                for order in trade_path:
                    try:
                        print(order)
                        base_currency = markets[order['market']]['base_currency']
                        quote_currency = markets[order['market']]['quote_currency']

                        marked_limit_price = float(mark_prices[base_currency])
                        exchange_rate = mark_prices[quote_currency] if quote_currency != global_quote_currency else 1
                        limit_price = marked_limit_price / float(exchange_rate)

                        txn_size = (account_value * trade['trade_percent']) / marked_limit_price

                        temp_order = {'market':order['market'],
                                      'trade_side':order['side'],
                                      'limit_price':limit_price,
                                      'amount':txn_size
                                      }

                        temp_orders.append(temp_order)
                    except:
                        #client.captureException()
                        logger.info('error occurred while processing order %s', order)
                        logger.error('Error thrown in trades_to_orders, processing an order', exc_info=True)

                orders.append(temp_orders)
            except:
                #client.captureException()
                logger.info('error occurred while processing trade %s', trade)
                logger.error('Error thrown in trades_to_orders, processing a trade', exc_info=True)

        # need/want to aggregate opposing orders within the same market
        # keep ordered orders intact
        return(orders)
    except:
        #client.captureException()
        logger.error('error thrown in trades_to_orders', exc_info=True)
    

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z
    
def local_available_markets(retry=True):
    max_retries = 5
    wait_time = 5 #seconds
    retries = 0
    while retries <= max_retries:
        
        target_exchange = xi.getSettings()['target_exchange']
        
        exchange_currencies = json.loads(xi.requestExchange(target_exchange,'currency')[target_exchange.upper()])
        
        excluded_currencies = xi.getSettings()['excluded_currencies']
        #universe = getSettings()['target_universe']
        
        #tradeable_currencies = exchange_currencies.pop(excluded_currencies)
        tradeable_currencies = list(exchange_currencies.keys())
        
        possible_markets = json.loads(xi.requestAvailableMarkets(coe_list=[{"exchange":target_exchange,"currencies":tradeable_currencies}])['availablemarkets'])
    
        raw_markets = {x:{'base_currency':x.split("/")[0], "quote_currency":x.split("/")[1]} for x in possible_markets}
        
        ticker = json.loads(xi.requestExchange(target_exchange,'ticker')[target_exchange.upper()])
        
        markets = {x:merge_two_dicts(y,ticker[x]) for x,y in raw_markets.items()}
        
        available_markets = {x:y for x,y in markets.items() if 'ERROR' not in y}
        
        for x,y in available_markets.items():
            available_markets[x]['price'] = (y['bid']+y['ask'])/2.0
    
        
        unavailable_markets= {x for x,y in raw_markets.items() if x not in available_markets}
        if len(available_markets) != 0:
            print("The following markets are being considered: ",list(available_markets.keys()))
            print("The following markets were listed but tickers were unavailable: ",unavailable_markets)
            return(available_markets)
            
        else:
            retries += 1
            print("No markets found. Waiting ",wait_time,"seconds before retry",retries,"of",max_retries)
            time.sleep(wait_time)
    print("No available markets were found. The following markets were listed but tickers were unavailable",
            unavailable_markets)
    return({})
    
def local_exchange_account(available_markets=None):
    
    if available_markets is None:
        available_markets = local_available_markets()
    
    user_settings = xi.getSettings()
    target_exchange = user_settings['target_exchange']
    creds = xi.getCreds(target_exchange)
    
    
    exchange_account = {'markets':available_markets,
                    'name':target_exchange,
                    'exchange_credentials':creds
    }
    return(exchange_account)
    
    
def local_current_holdings(exchange_account=None):
    
    if exchange_account is None:
        exchange_account = local_exchange_account()
    
    balances = xi.requestExchangeAccountBalance(exchange_account)
    current_holdings = {x:y['available']+y['frozen'] for x,y in balances['wallet'].items()}
    
    ##TODO: fix corresponding bug in exchange interface
    current_holdings['IOT'] = current_holdings.pop('IOTA', 0.0)
    
    return(current_holdings)
    

    
def local_mark_prices(available_markets=None):
    
    if available_markets is None:
        available_markets = local_available_markets()
    
    global_quote_currency = xi.getSettings()['global_quote_currency']
    
    mark_prices = calc_mark_prices(available_markets, global_quote_currency)
    print(mark_prices)
    return(mark_prices)


