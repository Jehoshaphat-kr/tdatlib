from tdatlib.dataset import market
from tdatlib.viewer import stock
from tdatlib.tdef import *

DEBUG_MARKET  = False
DEBUG_TREEMAP = False
DEBUG_STOCK   = True
DEBUG_GROUP   = False

if DEBUG_TREEMAP:
    krx = market.KR()
    treemap = krx.treemap(category='WICS', sub_category='1028')
    print(treemap)

if DEBUG_MARKET:
    krx = market.KR()
    krx.isetfokay()

if DEBUG_STOCK:
    viewer = stock.KR(
        ticker=신한지주,
        period=3
    )
    viewer.saveall()

if DEBUG_GROUP:
    # 은행 주식
    tickers = [KB금융, 하나금융지주, 우리금융지주, 신한지주, 기업은행]


    # tickers = ['000890', '186230', '149980', '024950', '276730', '033920']
    for ticker in tickers:
        myStock = stock.KR(ticker=ticker, period=3)
        myStock.saveall()