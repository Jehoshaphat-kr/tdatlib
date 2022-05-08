from datetime import datetime, timedelta
from pytz import timezone
from pykrx import stock
import yfinance as yf
import pandas as pd

class ohlcv(object):

    def __init__(
            self,
            ticker:str,
            name:str=str(),
            period:int=5,
            endate:str=str()
    ):
        self.ticker = ticker
        self.__name = name
        self.period = period
        self.endate = datetime.strptime(endate, "%Y%m%d") if endate else endate
        return

    @property
    def __raw__(self) -> pd.DataFrame:
        if hasattr(self, '__raw__'):
            return self.__getattribute__('__raw__')

        if self.ticker.isdigit():
            curr = datetime.now(timezone('Asia/Seoul' if self.ticker.isdigit() else 'US/Eastern'))
            prev = curr - timedelta(365 * self.period)
            func = stock.get_index_ohlcv_by_date if len(self.ticker) == 4 else stock.get_market_ohlcv_by_date
            raw = func(fromdate=prev.strftime("%Y%m%d"), todate=curr.strftime("%Y%m%d"), ticker=self.ticker)
            trade_stop = raw[raw.시가 == 0].copy()
            if not trade_stop.empty:
                raw.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop['종가']
        else:
            o_names = ['Open', 'High', 'Low', 'Close', 'Volume']
            c_names = ['시가', '고가', '저가', '종가', '거래량']
            raw = yf.Ticker(self.ticker).history(period=f'{self.period}y')[o_names]
            raw.index.name = '날짜'
            raw = raw.rename(columns=dict(zip(o_names, c_names)))
        self.__setattr__('__raw__', raw)
        return self.__getattribute__('__raw__')

    @property
    def name(self) -> str:
        if hasattr(self, '__name__'):
            return self.__getattribute__('__name__')

        if self.__name:
            self.__setattr__('__name__', self.__name)

        if self.ticker.isalpha():
            self.__setattr__('__name__', self.ticker)
        elif len(self.ticker) == 4:
            self.__setattr__('__name__', stock.get_index_ticker_name(ticker=self.ticker))
        elif len(self.ticker) == 6:
            _name = stock.get_market_ticker_name(ticker=self.ticker)
            if isinstance(_name, pd.DataFrame):
                self.__setattr__('__name__', stock.get_etf_ticker_name(ticker=self.ticker))
            self.__setattr__('__name__', stock.get_market_ticker_name(ticker=self.ticker))
        return self.__getattribute__('__name__')

    @property
    def currency(self) -> str:
        return 'USD' if self.ticker.isalpha() else 'KRW' if len(self.ticker) == 6 else '-'
