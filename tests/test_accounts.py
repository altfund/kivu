import pytest
import kivu

def test_mark_price():
    markets = {'A/B':{'base_currency':'A','quote_currency':'B','price':.5},
                'B/C':{'base_currency':'B','quote_currency':'C','price':3}}
    assert kivu.accounts.mark_price(base_currency='C',
                                    quote_currency='A',
                                    markets=markets) == 1.0/kivu.accounts.mark_price(base_currency='A',
                                    quote_currency='C',
                                    markets=markets)