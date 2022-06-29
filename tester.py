from tdatlib.dataset import market
from tdatlib.viewer import stock
from tdatlib.tdef import labels

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
        ticker=labels.우리금융지주,
        period=3
    )
    viewer.saveall()

if DEBUG_GROUP:
    for ticker in labels.banks:
        myStock = stock.KR(ticker=ticker, period=3)
        myStock.saveall()