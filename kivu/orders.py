def am_cancelLimitOrder( exchange, order_id):
    config = pyxi.getConfig()
    response = {}
    order_to_cancel = {}
    if exchange['name'].lower() == 'all':
        for exchange in exchanges:
            creds = {'exchange':exchange['name'].lower(),
                'key':exchange['creds']['key'],
                'secret':exchange['creds']['secret'],
                'passphrase':exchange['creds']['passphrase']
            }
            order_to_cancel.update({"exchange_credentials": creds});
            order_to_cancel.update({"order_id": order_id});
            r = pyxi.send(encrypt(order_to_cancel, config), "cancelorder", config)
            data = pyxi.decrypt(r)
            response.update({creds['exchange'].upper(): data})
    else:
        creds = {'exchange':creds['exchange'].lower(),
                'key':exchange['creds']['key'],
                'secret':exchange['creds']['secret'],
                'passphrase':exchange['creds']['passphrase']
            }
        order_to_cancel.update({"exchange_credentials": creds});
        order_to_cancel.update({"order_id": order_id});
        r = send(encrypt(order_to_cancel, config), "cancelorder", config)
        data = pyxi.decrypt(r)
        response.update({creds['exchange'].upper(): data})
    return response

def am_requestOpenOrders(creds):
    config = pyxi.getConfig()
    response = {}
    temp = {}
    r = pyxi.send(pyxi.encrypt(creds, config), "openorders", config)#, json=True)
    data = pyxi.decrypt(r)
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

    #pyxi.send(send(encrypt(exchange, config), method, config,json=False))
    for open_order in open_orders:
        result = pyxi.amCancelLimitOrder({'exchange_credentials':creds},dict(open_order)['id'])
        #'id': '1752063', 'orderId': '4d040e15-1236-473f-927d-c15d5c38a6fc'

        print(result)
#def am_requestLimitOrder(exchange, limit_order, order):
#    response = {}
#    config = pyxi.getConfig()
#    r = pyxi.send(encrypt(limit_order, config), "limitorder", config)
#    data = pyxi.decrypt(r)
#    response.update({exchange.upper(): data})
#    return(response)

#order = {'amount': 0.047004127026677146,
#   'limit_price': 761.155,
#   'market': 'ETH/USD',
#   'trade_side': 'BID'}
def make_orders(orders, exchange, txn_cost_percent = 0):
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
                    'key': exchange['creds']['key'],
                    'secret': exchange['creds']['secret'],
                    'passphrase': exchange['creds']['passphrase']
                },
                'order_specs': {
                   'base_currency': exchange['markets'][order['market']]['base_currency'],
                   'quote_currency': exchange['markets'][order['market']]['quote_currency'],
                   'volume': trimmed_volume,
                   'price': str(order["limit_price"]),
                   'test': False #not live_trading_on
                }
            }
            order_submission = pyxi.requestLimitOrder(exchange=exchange['name'],
                                                      limitorder=limit_order,
                                                      ordertype=order['trade_side'])
            print(order_submission)
        #return(order_submission)

def refresh_orders(exchange_orders, exchange):
    try:
        cancel_all_open_orders(exchange['creds'])
        make_orders(exchange_orders, exchange)
    except:
        client.captureException()
        logger.error('Error thrown in refresh_orders', exc_info=True)


def dummy_limit_order():

    limit_order = {
                    'altfund_id': uuid.uuid4().hex,
                    'order_type': order['trade_side'],
                    "order_id": "",
                    'exchange_credentials': {
                        'exchange': exchange['name'],
                        'key': exchange['creds']['key'],
                        'secret': exchange['creds']['secret'],
                        'passphrase': exchange['creds']['passphrase']
                    },
                    'order_specs': {
                       'base_currency': exchange['markets'][order['market']]['base_currency'],
                       'quote_currency': exchange['markets'][order['market']]['quote_currency'],
                       'volume': str(order["amount"]  * (1 - txn_cost_percent)),
                       'price': str(order["limit_price"]),
                       'test': False #not live_trading_on
                    }
                }

    order_submission = pyxi.requestLimitOrder(exchange=exchange['name'],
                                                      limitorder=limit_order,
                                                      ordertype=order['trade_side'])

    return(limit_order)