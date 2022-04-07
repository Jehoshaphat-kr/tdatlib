from tdatlib import ohlcv
import pandas as pd
import numpy as np


class series:

    __key = '종가'
    __rel_return = pd.DataFrame()
    
    def __init__(self, tickers:list or np.array, period:int=5):
        self.tickers, self.period = tickers, period
        for ticker in tickers:
            setattr(self, f'__{ticker}', ohlcv(ticker=ticker, period=period))
        return

    def set_key(self, key:str):
        self.__key = key
        return
    
    @property
    def rel_yield(self):
        """
        상대수익률 비교 데이터
        """
        if self.__rel_return.empty:
            objs = dict()
            for ticker in self.tickers:
                attr = getattr(self, f'__{ticker}')
                if not self.__key == '종가':
                    attr.set_key(key=self.__key)

                rel = attr.rel.copy()
                for col in rel.columns:
                    objs[(col, attr.name)] = rel[col]
            self.__rel_return = pd.concat(objs=objs, axis=1)
        return self.__rel_return

        


if __name__ == "__main__":
    # t_tickers = ['TSLA', 'MSFT', 'GOOG', 'ZM']
    t_tickers = ['005930', '000660', '058470', '032500']

    t_series = series(tickers=t_tickers, period=5)
    print(t_series.rel_yield)
    print(t_series.rel_yield['1Y'].dropna())


