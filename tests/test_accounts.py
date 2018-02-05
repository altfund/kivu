import pytest
import kivu

markets = {'A/B':{'base_currency':'A','quote_currency':'B','price':.5},
                'B/C':{'base_currency':'B','quote_currency':'C','price':3},
                'C/D':{'base_currency':'D','quote_currency':'C','price':2}
}

def test_calc_mark_price():
    assert kivu.accounts.calc_mark_price(base_currency='C',
                                    quote_currency='A',
                                    markets=markets) == 1.0/kivu.accounts.calc_mark_price(base_currency='A',
                                    quote_currency='C',
                                    markets=markets)
    
    assert kivu.accounts.calc_mark_price(base_currency='C',
                                    quote_currency='A',
                                    markets=markets) == 2/3.0
    
    assert kivu.accounts.calc_mark_price(base_currency='D',
                                    quote_currency='A',
                                    markets=markets) == 4/3.0
                                    
    assert kivu.accounts.calc_mark_price(base_currency='D',
                                    quote_currency='A',
                                    markets=markets) == 1.0/kivu.accounts.calc_mark_price(base_currency='A',
                                    quote_currency='D',
                                    markets=markets)
                                    
def test_calc_mark_prices():
    assert kivu.accounts.calc_mark_prices(markets, global_quote_currency="A") == {'A':1,'B':2,'C':2/3.0,'D':4/3.0}