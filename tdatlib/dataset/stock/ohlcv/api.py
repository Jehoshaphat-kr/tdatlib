from tdatlib.dataset.stock.ohlcv.toolbox import (
    fetch_ohlcv,
    calc_returns
)
from datetime import datetime
import pandas as pd


class technical(object):

    def __init__(self, ticker:str, period:int=5, endate:str=str()):
        self.ticker=ticker
        self.period=period
        self.endate=endate if not endate else datetime.strptime(endate, "%Y%m%d")
        return

    @property
    def ohlcv(self) -> pd.DataFrame:
        """
        :return:

                     시가   고가   저가   종가  거래량
        날짜
        2017-05-10  22000  22250  21300  21450  878239
        2017-05-11  21450  22000  21300  21450  853057
        2017-05-12  21450  21600  21250  21350  339716
        ...           ...    ...    ...    ...     ...
        2022-05-03  67700  68400  67200  67700  363237
        2022-05-04  68000  68200  67600  67900  252004
        2022-05-06  66700  67200  65700  66200  639829
        """
        if not hasattr(self, '__ohlcv'):
            __ohlcv = fetch_ohlcv(ticker=self.ticker, period=self.period)
            self.__setattr__('__ohlcv', __ohlcv[__ohlcv.index <= self.endate] if self.endate else __ohlcv)
        return self.__getattribute__('__ohlcv')

    @property
    def returns(self) -> pd.DataFrame:
        """
        :return:

                R1D   R1W   R1M    R3M    R6M    R1Y
        000990 -2.5 -1.49 -5.83 -10.54  12.97  17.79
        """
        return calc_returns(ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def backtest_answer(self) -> pd.DataFrame:
        if not hasattr(self, '__backtest_answer'):
            pass
        return self.__getattribute__('__backtest_answer')


if __name__ == "__main__":

    tech = technical(ticker='000990')

    print(tech.ohlcv)
    print(tech.returns)