import pytest
from kivu import *

#@pytest.fixture
#def weights_equal(assets, weights, should_weights, method):
#   test_weights = {x:y for x,y in zip(assets,weights)}
#   should_be = {x:y for x,y in zip(assets,should_weights)}
#   portfolios.[method](test_weights, should_be)
#   return()


def test_calculate_even_weights():
    assert portfolios.calculate_even_weights(['A','B']) == {'A':.5,'B':.5}
    
def test_normalize_weights():
    #test_assets = ['A','B']
    #test_weights = [1,1]
    test_weights = {'A':1,'B':1}
    should_be = {'A':.5,'B':.5}
    assert portfolios.normalize_weights(test_weights) == should_be
    
    test_weights = {'A':0,'B':0}
    should_be = {'A':0,'B':0}
    assert portfolios.normalize_weights(test_weights) == should_be
    