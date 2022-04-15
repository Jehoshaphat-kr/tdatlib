from tdatlib.fetch.stock import (
    _ohlcv, _fnguide, _comm
)
import pandas as pd
from inspect import currentframe as inner


class ohlcv(_comm.comm):

    def __init__(self, ticker:str, name:str=str(), period:int=5):
        super().__init__(ticker=ticker, name=name)
        self.period = period
        return

    @property
    def ohlcv(self) -> pd.DataFrame:
        """
        시가 / 고가 / 저가 / 종가 / 거래량
        :return:
                     시가   고가   저가   종가     거래량
        날짜
        2017-04-17  42000  42080  41520  41560    104495
        2017-04-18  41680  41820  41280  41500    137213
        2017-04-19  41299  41420  40900  40900    235258
        ...           ...    ...    ...    ...       ...
        2022-04-13  67300  69000  67200  68700  17378619
        2022-04-14  68700  68700  67500  67500  16409494
        2022-04-15  67200  67300  66500  66700   8569557
        """
        if not hasattr(self, '__ohlcv'):
            self.__setattr__('__ohlcv', _ohlcv.fetch_ohlcv(ticker=self.ticker, period=self.period))
        return self.__getattribute__('__ohlcv')


class fundamental(_comm.comm, _fnguide.fnguide):
    pass


if __name__ == "__main__":
    t_ticker = '005930'
    tester = ohlcv(ticker=t_ticker)

    print(tester.name)
    print(tester.ohlcv)

