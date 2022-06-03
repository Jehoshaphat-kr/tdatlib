from tdatlib.dataset import market
from tdatlib.viewer import stock

DEBUG_MARKET = True
DEBUG_STOCK  = False

if DEBUG_MARKET:
    krx = market.KR()
    krx.isetfokay()

if DEBUG_STOCK:
    ticker = '170030'
    viewer = stock.KR(ticker=ticker, period=3)
    viewer.saveall()