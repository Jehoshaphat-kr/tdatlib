from tdatlib.dataset.stock import (
    KR as _kr,
    US as _us
)
from tdatlib.archive.deprecated.viewer.stock.ohlcv import ohlcv
from tdatlib.archive.deprecated.viewer.stock import value
from tdatlib.archive.deprecated.viewer.stock import view_compare


class KR(object):
    def __init__(self, ticker:str, period:int=5, endate:str=str()):
        _src = _kr(ticker=ticker, period=period, endate=endate)
        self.technical = ohlcv(src=_src)
        self.fundamental = value(src=_src)
        self.relatives = view_compare(tickers=self.fundamental.src.relatives[1], period=period)
        return

    def saveall(self, path:str=str()):
        self.technical.saveall(path=path)
        self.fundamental.saveall(path=path)
        self.relatives.saveall(tag=self.technical.tag, path=path)
        return


class US(object):
    def __init__(self, ticker:str, period:int=5, endate:str=str()):
        _src = _us(ticker=ticker, period=period, endate=endate)
        self.technical = ohlcv(src=_src)
        return

    def saveall(self, path:str=str()):
        self.technical.saveall(path=path)
        return