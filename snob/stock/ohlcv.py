from pykrx.stock import (
    get_market_ohlcv_by_date,
    get_market_ticker_name,
    get_etf_ticker_name
)
from datetime import datetime, timedelta
from pytz import timezone
import yfinance as yf
import pandas as pd
import numpy as np
import warnings


warnings.simplefilter(action='ignore', category=FutureWarning)
np.seterr(divide='ignore', invalid='ignore')


class _ohlcv(object):

    __period = 20
    def __init__(self, ticker:str, basis:pd.DataFrame=None):
        self.ticker = ticker
        self.curr = 'USD' if ticker.isalpha() else 'KRW'
        self.base = basis
        return

    @property
    def period(self) -> int:
        return self.__period

    @period.setter
    def period(self, period:int):
        self.__period = period

    @property
    def name(self) -> str:
        if not hasattr(self, '__name'):
            if self.ticker.isalpha():
                self.__setattr__('__name', self.ticker)
            elif isinstance(self.base, pd.DataFrame):
                self.__setattr__('__name', self.base.loc[self.ticker, '종목명'])
            else:
                name = get_market_ticker_name(ticker=self.ticker)
                if isinstance(name, pd.DataFrame):
                    self.__setattr__('__name', get_etf_ticker_name(ticker=self.ticker))
                else:
                    self.__setattr__('__name', name)
        return self.__getattribute__('__name')

    @property
    def ohlcv(self) -> pd.DataFrame:
        if not hasattr(self, f'__ohlcv_{self.period}'):
            curr = datetime.now(timezone('Asia/Seoul' if self.ticker.isdigit() else 'US/Eastern'))
            prev = curr - timedelta(365 * self.period)
            if self.ticker.isdigit():
                ohlcv = get_market_ohlcv_by_date(
                    fromdate=prev.strftime("%Y%m%d"),
                    todate=curr.strftime("%Y%m%d"),
                    ticker=self.ticker
                )
                trade_stop = ohlcv[ohlcv.시가 == 0].copy()
                if not trade_stop.empty:
                    ohlcv.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop['종가']
            else:
                o_names = ['Open', 'High', 'Low', 'Close', 'Volume']
                c_names = ['시가', '고가', '저가', '종가', '거래량']
                ohlcv = yf.Ticker(self.ticker).history(period=f'{self.period}y')[o_names]
                ohlcv.index.name = '날짜'
                ohlcv = ohlcv.rename(columns=dict(zip(o_names, c_names)))
            self.__setattr__(f'__ohlcv_{self.period}', ohlcv)
        return self.__getattribute__(f'__ohlcv_{self.period}')


if __name__ == "__main__":
    tester = _ohlcv(ticker='000990')

    # print(tech.ohlcv)
    # print(tech.ohlcv_bt)
    # print(tech.ohlcv_btr)
    # print(tech.ohlcv_returns)
    # print(tech.ohlcv_ta)
    # print(tech.ohlcv_rr)
    # print(tech.ohlcv_dd)
    # print(tech.ohlcv_sma)
    # print(tech.ohlcv_ema)
    # print(tech.ohlcv_iir)
    # print(tech.ohlcv_cagr)
    # print(tech.ohlcv_volatility)
    # print(tech.ohlcv_fiftytwo)
    # print(tech.ohlcv_trend)
    # print(tech.ohlcv_bound)