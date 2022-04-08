from inspect import currentframe as inner
from tdatlib import ohlcv
import pandas as pd
import numpy as np


class series:

    def __init__(self, tickers:list or np.array, period:int=5):
        self.tickers, self.period = tickers, period
        for ticker in tickers:
            setattr(self, f'__{ticker}', ohlcv(ticker=ticker, period=period))
        return

    @property
    def rel_yield(self):
        """
        상대수익률 비교 데이터
        """
        objs = dict()
        for ticker in self.tickers:
            attr = self.__getattribute__(f'__{ticker}')
            rel = attr.relative_return.copy()
            for col in rel.columns:
                objs[(col, attr.name)] = rel[col]
        return pd.concat(objs=objs, axis=1)


if __name__ == "__main__":
    # t_tickers = ['TSLA', 'MSFT', 'GOOG', 'ZM']
    t_tickers = ['005930', '000660', '058470', '032500']

    t_series = series(tickers=t_tickers, period=5)
    print(t_series.rel_yield)
    print(t_series.rel_yield['1Y'].dropna())


