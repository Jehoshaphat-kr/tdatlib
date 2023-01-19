from snob.stock.ohlcv import _ohlcv
from snob.stock.fnguide import _fnguide
import pandas as pd


class kr(_ohlcv):
    def __init__(self, ticker:str, basis:pd.DataFrame=None):
        super().__init__(ticker=ticker, basis=basis)
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
    print(kr.fnguide.RecentProducts)
