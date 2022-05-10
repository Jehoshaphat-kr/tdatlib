from tdatlib.dataset.stock.ohlcv import technical


class KR(technical):
    def __init__(self, ticker:str, period:int=5, endate:str=str()):
        super().__init__(ticker=ticker, period=period, endate=endate)
        return


class US(technical):
    def __init__(self, ticker:str, period:int=5, endate:str=str()):
        super().__init__(ticker=ticker, period=period, endate=endate)
        return