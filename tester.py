from tdatlib.dataset import market, index
from tdatlib.viewer import stock
from tdatlib.tdef import labels
import os

DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
DEBUG_TREEMAP = False
DEBUG_MARKET  = False
DEBUG_INDEX   = True
DEBUG_STOCK   = False
DEBUG_GROUP   = False

if DEBUG_TREEMAP:
    krx = market.KR()
    treemap = krx.treemap(category='WICS', sub_category='1028')
    print(treemap)

if DEBUG_MARKET:
    krx = market.KR()
    krx.isetfokay()

if DEBUG_INDEX:
    idx = index.overall()
    print(idx.kind)

if DEBUG_STOCK:
    viewer = stock.KR(
        ticker=labels.우리금융지주,
        period=3
    )
    viewer.saveall()

if DEBUG_GROUP:
    for ticker in labels.은행:
        myStock = stock.KR(ticker=ticker, period=3)
        myStock.saveall()