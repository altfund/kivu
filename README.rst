Setup
-------------
Start an XI

``
git clone [this repo]
cd kivu
virtualenv --python=python3 env
source env/bin/activate
pip install .
pytest
cp config_template config
``

Then fill in the config. Some example `[settings]` for use later:

``
[settings]
xi_url=http://localhost:9000
aes_key=0123456789101112
test=True
target_exchange=binance
target_universe=[ETH,NEO]
excluded_currencies=[]
tolerance_percent=0
global_quote_currency=USD
``

you can use invoke for everything you're used to (with no more :
``invoke invoke symbols -e GDAX``

pyxi's methods are in the exchanges directory (verbatim, for backward compatibility):

- ``kivu.exchanges.xi.decrypt()``
- ``kivu.exchanges.ccxt.CcxtClient()``

AM's non-django-specific logic is in the remaining files (which correspond to their respective x_manager/utils.py from AM):

- ``portfolios.py``: ``kivu.portfolios.calculate_altfundx_weights()``
- ``accounts.py``: ``kivu.accounts.percentagize()``
- ``orders.py``: ``kivu.orders.cancel_all_open_orders()``

``backtests.py`` is a work in progress.

Rebalancing from the command line
===================================
``invoke equal-rebalance``: rebalances to an equal notional value in each asset in the universe, as specified in config settings


ToDos
=======

- add ``-e`` to ``invoke equal-rebalance`` instead of/addition to using ``target_exchange`` config setting
- slam rebalancing against a bunch of exchanges and get it to run smoothly
