#!/bin/python3

import json
import re
import random
import base64
import string
import os
import configparser

from Crypto.Cipher import AES
from invoke import task

import kivu

#balance, cancelorder, limitorder, openorders, orderbook, json, ticker, tradefees, tradehistory,

#exchanges = ['KRAKEN', 'BITFINEX', 'POLONIEX', 'GDAX', 'TRUEFX']
exchanges = ['GDAX', 'KRAKEN', 'POLONIEX', 'BITFINEX', 'VAULTORO', 'TRUEFX', 'QUADRIGACX', 'LUNO', 'GEMINI', 'YOBIT', 'LIVECOIN', 'VIRCUREX', 'HUOBI', 'GATECOIN', 'THEROCK', 'RIPPLE', 'QUOINE', 'TAURUS', 'JUBI', 'MERCADOBITCOIN', 'OKCOIN', 'POLONIEX', 'PAYMIUM', 'HITBTC', 'LAKEBTC', 'INDEPENDENTRESERVE', 'ITBIT', 'GDAX', 'KRAKEN', 'EMPOEX', 'DSX', 'CRYPTONIT', 'CRYPTOPIA', 'CRYPTOFACILITIES', 'COINMATE', 'COINFLOOR', 'COINBASE', 'CHBTC', 'CEXIO', 'CCEX', 'CAMPBX', 'BTER', 'BTCTRADE', 'BTCMARKETS', 'BTCE', 'BTCC', 'BTC38', 'BLOCKCHAIN', 'BLEUTRADE', 'BITTREX', 'BITSTAMP', 'BITSO', 'BITMARKET', 'BITFINEX', 'BITCUREX', 'BITCOINIUM', 'BITCOINDE', 'BITCOINCORE', 'BITCOINCHARTS', 'BITCOINAVERAGE', 'BITBAY', 'ANX']
default_limit_ask = {"order_type":"ASK","order_specs":{"base_currency":"ETH","quote_currency":"BTC","volume":"0.1","price":"10000","test":True}}
default_limit_bid = {"order_type":"BID","order_specs":{"base_currency":"ETH","quote_currency":"BTC","volume":"0.01","price":"0.0001","test": True}}

def getCreds(exchange):
    exchange = exchange.upper()
    config = configparser.ConfigParser()
    config.read('config')
    try:
        creds = {
                "exchange": exchange.lower(),
                "key": config[exchange]['key'],
                "secret": config[exchange]['secret']
                }
    except:
        raise ValueError('exchange ' + exchange.lower() + ' does not have credentials')

    try:
        passphrase = config[exchange]['passphrase']
        creds.update({"passphrase":  passphrase})
        return creds
    except:
        return creds

def report(data, dump=False):
    try:
        for key, value in data.items():
            #if (value == None or 'ERROR' in value or 'exception' in value or 'error' in value or re.match(r'.*error.*', value.lower()) or re.match(r'.*redacted.*', value.lower()) or len(value) < 3): response.update({"error": True})
            #    print_exchange_report(key, value, dump)
            #else:
            print("==============================================================")
            print(key)
            print("==============================================================")
            print(value)
    except Exception as e:
        print(data)

def print_report( response, dump ):
    if dump:
        print("==============================================================")
        print("DUMP")
        print("==============================================================")
        print(response)
        print("==============================================================")
        print("END DUMP")
        print("==============================================================")
        print("")
        print("")

    print("==============================================================")
    print("START INDIVIDUAL EXCHANGES")
    print("==============================================================")
    if ('error' in response):
        failures = print_exchange_results(response, True)
        print("==============================================================")
        print("FAILURE(S): ", len(failures)/len(exchanges)*100,"%, :: ", len(failures),"/", len(exchanges))
        print(failures)
        print("==============================================================")
    else:
        print_exchange_results(response, False)
        print("==============================================================")
        print("SUCCESS")
        print("==============================================================")

def print_exchange_results(response, failure):
    failures = []
    for exchange in exchanges:
        if exchange.upper() + "ret" in response:
            print("+++++++++++++++++++++++++++++")
            print(exchange.upper())
            print("~~~~~~~~~~~~~~~~")
            print(response.get(exchange.upper()))
            if response.get(exchange.upper() + "ret"):
                print("SUCCESS")
                print(len(response.get(exchange.upper())))
            else:
                failures.append(exchange.upper())
                print("FAILURE")
            print("+++++++++++++++++++++++++++++")
    return failures

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges"})
def balance(name, exchange):
    response = kivu.exchanges.xi.localRequestBalance(exchange)
    report(response)

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges"})
def symbols(name, exchange):
    response = kivu.exchanges.xi.requestExchange(exchange, 'exchangesymbols')
    report(response)

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges"})
def tradehistory(name, exchange):
    response = kivu.exchanges.xi.requestTradeHistory(exchange)
    report(response)

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges"})
def fundinghistory(name, exchange):
    exchange_creds = getCreds(exchange)
    exchange = {"exchange_credentials": exchange_creds};
    response = kivu.exchanges.xi.requestFundingHistory(exchange, "fundinghistory")
    print(json.loads(response))

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges"})
def openorders(name, exchange):
    response = kivu.exchanges.xi.requestOpenOrders(exchange)
    report(response)

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges", 'base': "give -b base currency", 'quote': "give -q quote currency"})
def requestOpenOrdersSymbol(name, exchange, base, quote):
    response = kivu.exchanges.xi.requestOpenOrders(exchange, base=base, quote=quote)
    report(response)

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges"})
def symbolmetadata(name, exchange):
    response = kivu.exchanges.xi.requestExchange(exchange, 'exchangesymbolsmetadata' )
    print(response)

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges"})
def ticker(name, exchange):
    response = kivu.exchanges.xi.requestExchange(exchange, 'ticker')
    report(response)

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges", "base": "-b the base currency, e.g. BTC", "quote": "-q the quote currency, e.g. ETH"})
def orderbook(name, exchange, base, quote):
    response = kivu.exchanges.xi.requestOrderBook('orderbook', exchange, base, quote)
    report(response)

def jsonendpoint(name):
    response = kivu.exchanges.xi.requestExchange(exchanqe, 'json')
    report(response)

@task(help={'exchange': "-e name of EXCHANGE or all for all exchanges", "ordertype": "-o ASK or BID", "base_currency": "-b the base currency, e.g. BTC", "quote_currency": "-q the quote currency, e.g. ETH", "volume": "-v volume of base currency", "price": "-p price of quote currency", "test": "-t is test true/t runs in verify mode, or false/f runs in production mode" })
def limitorder(name, exchange, ordertype, base, quote, volume, price, test):
    if (test.lower() == "true"):
        test = True
    else:
        test = False

    if exchange.lower() == 'all':
        for exchange in exchanges:
            limit_order = {"order_type":ordertype.upper(),"order_specs":{"base_currency":base.upper(),"quote_currency":quote.upper(),"volume":volume,"price":price,"test":test}}
            creds = getCreds(exchange)
            limit_order.update({"exchange_credentials":creds})
            response = kivu.exchanges.xi.requestLimitOrder(exchange,limit_order, ordertype)
            report(response)
    else:
        limit_order = {"order_type":ordertype.upper(),"order_specs":{"base_currency":base.upper(),"quote_currency":quote.upper(),"volume":volume,"price":price,"test":test}}
        creds = getCreds(exchange)
        limit_order.update({"exchange_credentials":creds})
        response = kivu.exchanges.xi.requestLimitOrder(exchange,limit_order, ordertype)
        report(response)

@task(help={'exchange': "-e names of two exchanges for inter exchange arbitrage, comma separated list, no spaces, this applies to all parameters, order in each list to each paramter of this method  corresponsds to first or second order", "ordertype": "-o ASK or BID", "base_currency": "-b the base currency, e.g. BTC", "quote_currency": "-q the quote currency, e.g. ETH", "volume": "-v volume of base currency", "price": "-p price of quote currency", "test": "-t is test true/t runs in verify mode, or false/f runs in production mode" })
def fillorkill(name, exchange, ordertype, base, quote, volume, price, test):
    exchange_arr = exchange.split(',');
    ordertype_arr = ordertype.split(',');
    base_arr = base.split(',');
    quote_arr = quote.split(',');
    volume_arr = volume.split(',');
    price_arr = price.split(',');
    test_arr = test.split(',');
    orders = []

    index = 0;
    while (index < len(exchange_arr)):
        test = True
        if (test_arr[index].lower() == "true"):
            test = True
        else:
            test = False

        limit_order = {"order_type":ordertype_arr[index].upper(), "order_specs": {"base_currency":base_arr[index].upper(), "quote_currency":quote_arr[index].upper(), "volume":volume_arr[index], "price":price_arr[index], "test":test}}
        order_on_exchange = {"exchange": exchange_arr[index],"order": limit_order}
        orders.append(order_on_exchange)
        index = index + 1

    response = kivu.exchanges.xi.requestFillOrKill(orders)
    print(response)

@task(help={'exchange': "-e names of two exchanges for inter exchange arbitrage, comma separated list, no spaces, this applies to all parameters, order in each list to each paramter of this method  corresponsds to first or second order", "ordertype": "-o ASK or BID", "base_currency": "-b the base currency, e.g. BTC", "quote_currency": "-q the quote currency, e.g. ETH", "volume": "-v volume of base currency", "price": "-p price of quote currency", "test": "-t is test true/t runs in verify mode, or false/f runs in production mode" })
def iea(name, exchange, ordertype, base, quote, volume, price, test):
    exchange_arr = exchange.split(',');
    ordertype_arr = ordertype.split(',');
    base_arr = base.split(',');
    quote_arr = quote.split(',');
    volume_arr = volume.split(',');
    price_arr = price.split(',');
    test_arr = test.split(',');
    orders = []

    index = 0;
    while (index < len(exchange_arr)):
        test = True
        if (test_arr[index].lower() == "true"):
            test = True
        else:
            test = False

        limit_order = {"order_type":ordertype_arr[index].upper(), "order_specs": {"base_currency":base_arr[index].upper(), "quote_currency":quote_arr[index].upper(), "volume":volume_arr[index], "price":price_arr[index], "test":test}}
        order_on_exchange = {"exchange": exchange_arr[index],"order": limit_order}
        orders.append(order_on_exchange)
        index = index + 1

    response = kivu.exchanges.xi.requestInterExchangeArbitrage(orders)

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges"})
def isfeasible(name, exchange):
    response = kivu.exchanges.xi.requestExchange(exchange, 'isfeasible')
    report(response)


@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges"})
def currency(name, exchange):
    response = kivu.exchanges.xi.requestExchange(exchange, 'currency')
    report(response)

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges", "order_id": "give -o id of order to cancel", "symbol": "give -s to provide market order should be canceled on."})
def cancelorderSymbol(name, exchange, order_id, symbol):
    response = kivu.exchanges.xi.cancelLimitOrder(exchange, order_id, symbol)
    report(response)

@task(help={'exchange': "give -e name of EXCHANGE or ALL for all exchanges", "order_id": "give -o id of order to cancel"})
def cancelorder(name, exchange, order_id):
    response = kivu.exchanges.xi.cancelLimitOrder(exchange, order_id)
    report(response)

@task(help={"exchange": "give -e the exchange ", "orders": "give -o comma separated list (no spaced) or order ids"})
def getorders(name, exchange, orders):
    orders_arr = orders.split(',');
    response = kivu.exchanges.xi.requestOrders(exchange, orders_arr)
    report(response)

@task(help={"quote": "give -q symbol of quote currency", "base": "give -b symbol of base currency", 'exchange': "give -e comma separated list of exchanges, no spaces "})
def aggregateorderbooks(name, base, quote, exchanges):
    exchanges_arr = exchanges.split(',');
    response = kivu.exchanges.xi.requestAggregateOrderBooks(base, quote, exchanges_arr)
    report(response)

@task(help={"quote": "give -q symbol of quote currency", "base": "give -b symbol of base currency", 'exchange': "give -e comma separated list of exchanges, no spaces "})
def aggregateallorderbooks(name, base, quote):
    #exchanges_arr = exchanges.split(',');
    exchanges_arr = []
    for x in exchanges:
        exchanges_arr.append(x.lower())
    response = kivu.exchanges.xi.requestAggregateOrderBooks(base, quote, exchanges_arr)
    report(response)

@task(help={"exchanges": "give -e, comma separated list,i no spaces", "currencylists": "give -c comma separated list of forward slash separated list of currencies i.e. ETH/BTC/LTC,LTC/BTC/XRP/ETH. In this example, the user would have provided two exchanges and the first list of currencies separated by the forward slash would correspond to the fist exchange, and the second list of currencies separated by the forward slash (the list of currencies after the comma) would refer to the second exchange"})
def availablemarkets(name, exchanges, currencylists):
    exchanges_arr = exchanges.split(',');
    currencies_arr = currencylists.split(',');
    coe_list = []
    if len(exchanges_arr) == len(currencies_arr):
        count = 0
        while (count < len(exchanges_arr)):
            currency_on_exchange = {"exchange": exchanges_arr[count],
                                  "currencies": currencies_arr[count].split('/')}
            coe_list.append(currency_on_exchange)
            count += 1
        response = kivu.exchanges.xi.requestAvailableMarkets(coe_list)
        report(response)
    else:
        print("Error must supply 1:1 relationship between kivu.exchanges.xi.requested exchanges and currencies")


@task
def ls(name):
    for x in exchanges:
        print(x)

@task
def equal_rebalance(name):
    
    user_settings = kivu.exchanges.xi.getSettings()
    
    available_markets = kivu.accounts.local_available_markets()
    exchange_account = kivu.accounts.local_exchange_account(available_markets=available_markets)
    current_holdings = kivu.accounts.local_current_holdings(exchange_account)
    weights = kivu.portfolios.local_even_weights()
    mark_prices = kivu.accounts.local_mark_prices(available_markets=available_markets)
    global_quote_currency = user_settings['global_quote_currency']
    tolerance_percent = float(user_settings['tolerance_percent'])
    
    orders_to_rebalance = kivu.accounts.percentage_rebalance(exchange=exchange_account,
                                            current_holdings=current_holdings,
                                            weights=weights, 
                                            mark_prices=mark_prices, 
                                            global_quote_currency=global_quote_currency,
                                            tolerance_percent=tolerance_percent)
    
    print(orders_to_rebalance)
    
    #kivu.orders.refresh_orders(orders_to_rebalance, exchange_account, test=bool(user_settings['test']))

@task
def fetch_markets(name):
    kivu.accounts.local_available_markets()

@task    
def fetch_ticker(name):
    marked_markets = kivu.accounts.calc_mark_prices(bonux.local_available_markets(), global_quote_currency='USD')
    print(marked_markets)
    
@task
def fetch_current_holdings(name):
    current_holdings = kivu.accounts.local_current_holdings()
    print(current_holdings)