from tdatlib.stock.ohlcv import _ohlcv
from tdatlib.stock.fnguide import _fnguide


class kr(_ohlcv):
    def __init__(self, ticker:str):
        super().__init__(ticker=ticker)
        self.fnguide = _fnguide(ticker=ticker)
        return


class us(_ohlcv):
    def __init__(self, ticker:str):
        super().__init__(ticker=ticker)
        return


if __name__ == "__main__":
    kr = kr(ticker='316140')
    print(kr.name)
    print(kr.ohlcv)
    print(kr.fnguide.Products)
