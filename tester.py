from tdatlib.dataset import market
from tdatlib.viewer import stock

DEBUG_MARKET  = False
DEBUG_TREEMAP = True
DEBUG_STOCK   = False
DEBUG_GROUP   = False

if DEBUG_TREEMAP:
    krx = market.KR()
    treemap = krx.treemap(category='WICS', sub_category='1028')
    print(treemap)

if DEBUG_MARKET:
    krx = market.KR()
    krx.isetfokay()

if DEBUG_STOCK:
    ticker = '170030'
    viewer = stock.KR(ticker=ticker, period=3)
    viewer.saveall()

if DEBUG_GROUP:
    tickers = ['000890', '186230', '149980', '024950', '276730', '033920']
    for ticker in tickers:
        myStock = stock.KR(ticker=ticker, period=3)
        myStock.saveall()