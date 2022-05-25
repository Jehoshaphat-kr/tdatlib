from tdatlib.dataset.stock import (
    KR as _kr,
    US as _us
)

class KR(object):

    def __init__(self, ticker:str, period:int=5, endate:str=str()):
        _src = _kr(ticker=ticker, period=period, endate=endate)