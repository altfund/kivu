import json
import uuid

import logging
logger = logging.getLogger('local')

from .exchanges import xi, ccxt


def am_cancelLimitOrder( exchange, order_id):
    config = xi.getConfig()
    response = {}
    order_to_cancel = {}
    if exchange['name'].lower() == 'all':
        for exchange in xi.active_exchanges:
            creds = {'exchange':exchange['name'].lower(),
                'key':exchange['exchange_credentials']['key'],
                'secret':exchange['exchange_credentials']['secret'],
                'passphrase':exchange['exchange_credentials']['passphrase']
            }
            order_to_cancel.update({"exchange_credentials": creds});
            order_to_cancel.update({"order_id": order_id});
            r = xi.send(xi.encrypt(order_to_cancel, config), "cancelorder", config)
            data = xi.decrypt(r)
            response.update({creds['exchange'].upper(): data})
    else:
        creds = {'exchange':creds['exchange'].lower(),
                'key':exchange['exchange_credentials']['key'],
                'secret':exchange['exchange_credentials']['secret'],
                'passphrase':exchange['exchange_credentials']['passphrase']
            }
        order_to_cancel.update({"exchange_credentials": creds});
        order_to_cancel.update({"order_id": order_id});
        r = xi.send(xi.encrypt(order_to_cancel, config), "cancelorder", config)
        data = xi.decrypt(r)
        response.update({creds['exchange'].upper(): data})
    return response

def am_requestOpenOrders(creds):
    config = xi.getConfig()
    response = {}
    temp = {}
    r = xi.send(xi.encrypt(creds, config), "openorders", config)#, json=True)
    data = xi.decrypt(r)
    response.update({creds['exchange'].upper(): data})
    print(data)
    print(type(data))
    return response

def cancel_all_open_orders(creds):
    result = False
    open_orders = json.loads(am_requestOpenOrders(creds)[creds['exchange'].upper()])
    print(open_orders)

    if open_orders is None:
        return ( True )

    if (len(open_orders)==0):
        return ( True )

    #xi.send(send(encrypt(exchange, config), method, config,json=False))
    for open_order in open_orders:
        result = xi.amCancelLimitOrder({'exchange_credentials':creds},dict(open_order)['id'])
        #'id': '1752063', 'orderId': '4d040e15-1236-473f-927d-c15d5c38a6fc'

        print(result)
#def am_requestLimitOrder(exchange, limit_order, order):
#    response = {}
#    config = xi.getConfig()
#    r = xi.send(encrypt(limit_order, config), "limitorder", config)
#    data = xi.decrypt(r)
#    response.update({exchange.upper(): data})
#    return(response)

#order = {'amount': 0.047004127026677146,
#   'limit_price': 761.155,
#   'market': 'ETH/USD',
#   'trade_side': 'BID'}
def make_orders(orders, exchange, txn_cost_percent = 0, test=True):
    for order_set in orders:
        if len(order_set)>0:
            order = order_set[0]
            print(order)
            trimmed_volume = str(order["amount"]  * (1 - txn_cost_percent))
            limit_order = {
                'altfund_id': uuid.uuid4().hex,
                'order_type': order['trade_side'],
                "order_id": "",
                'exchange_credentials': {
                    'exchange': exchange['name'],
                    'key': exchange['exchange_credentials']['key'],
                    'secret': exchange['exchange_credentials']['secret'],
                    'passphrase': exchange['exchange_credentials']['passphrase']
                },
                'order_specs': {
                   'base_currency': exchange['markets'][order['market']]['base_currency'],
                   'quote_currency': exchange['markets'][order['market']]['quote_currency'],
                   'volume': trimmed_volume,
                   'price': str(order["limit_price"]),
                   'test': test
                }
            }
            order_submission = xi.requestLimitOrder(exchange=exchange['name'],
                                                      limitorder=limit_order,
                                                      ordertype=order['trade_side'])
            print(order_submission)
        #return(order_submission)

def refresh_orders(exchange_orders, exchange,test=True):
    try:
        cancel_all_open_orders(exchange['exchange_credentials'])
        make_orders(exchange_orders, exchange)
    except:
        #client.captureException()
        logger.error('Error thrown in refresh_orders', exc_info=True)


def dummy_limit_order():

    limit_order = {
                    'altfund_id': uuid.uuid4().hex,
                    'order_type': order['trade_side'],
                    "order_id": "",
                    'exchange_credentials': {
                        'exchange': exchange['name'],
                        'key': exchange['exchange_credentials']['key'],
                        'secret': exchange['exchange_credentials']['secret'],
                        'passphrase': exchange['exchange_credentials']['passphrase']
                    },
                    'order_specs': {
                       'base_currency': exchange['markets'][order['market']]['base_currency'],
                       'quote_currency': exchange['markets'][order['market']]['quote_currency'],
                       'volume': str(order["amount"]  * (1 - txn_cost_percent)),
                       'price': str(order["limit_price"]),
                       'test': False #not live_trading_on
                    }
                }

    order_submission = xi.requestLimitOrder(exchange=exchange['name'],
                                                      limitorder=limit_order,
                                                      ordertype=order['trade_side'])

    return(limit_order)