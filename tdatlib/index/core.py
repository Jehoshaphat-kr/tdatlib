from datetime import datetime, timedelta
from tdatlib.index._graph import _trace
from pykrx.stock import (
    get_index_ticker_list,
    get_index_ticker_name,
    get_index_portfolio_deposit_file,
    get_index_ohlcv_by_date
)
import pandas as pd


class _fetch(object):

    __today = datetime.now().date()
    __period = 20
    __trading_date = None

    @property
    def period(self) -> int:
        return self.__period

    @period.setter
    def period(self, period: int):
        self.__period = period

    @property
    def trading_date(self) -> str:
        return self.__trading_date

    @trading_date.setter
    def trading_date(self, trading_date: str):
        self.__trading_date = trading_date

    @property
    def kind(self) -> pd.DataFrame:
        """
        :return:
                          KOSPI                                KOSDAQ               KRX                      테마
            지수         지수명   지수                         지수명  지수      지수명  지수              지수명
        0   1001         코스피   2001                         코스닥  5042     KRX 100  1163    코스피 고배당 50
        1   1002  코스피 대형주   2002                  코스닥 대형주  5043  KRX 자동차  1164  코스피 배당성장 50
        2   1003  코스피 중형주   2003                  코스닥 중형주  5044  KRX 반도체  1165  코스피 우선주 지수
        ...  ...            ...    ...                            ...   ...        ...    ...                 ...
        47   NaN            NaN   2216            코스닥 150 정보기술   NaN        NaN    NaN                 NaN
        48   NaN            NaN   2217            코스닥 150 헬스케어   NaN        NaN    NaN                 NaN
        49   NaN            NaN   2218  코스닥 150 커뮤니케이션서비스   NaN        NaN    NaN                 NaN
        """
        objs = dict()
        for market in ('KOSPI', 'KOSDAQ', 'KRX', '테마'):
            indices = get_index_ticker_list(date=self.__trading_date, market=market)
            names = [get_index_ticker_name(index) for index in indices]
            objs[market] = pd.DataFrame(data={'지수': indices, '지수명': names})
        return pd.concat(objs=objs, axis=1)

    def ohlcv(self, ticker:str) -> pd.DataFrame:
        end = self.trading_date if self.trading_date else self.__today.strftime("%Y%m%d")
        start = datetime.strptime(end, "%Y%m%d") - timedelta(self.period * 365)
        return get_index_ohlcv_by_date(fromdate=start.strftime("%Y%m%d"), todate=end, ticker=ticker)

    def deposit(self, ticker: str) -> list:
        return get_index_portfolio_deposit_file(ticker, date=self.__trading_date)



class data(_fetch):

    def __init__(self):
        self.trace = _trace(self)
        return

    @property
    def kospi(self) -> pd.DataFrame:
        if not hasattr(self, '__kospi'):
            self.__setattr__('__kospi', self.ohlcv(ticker='1001'))
        return self.__getattribute__('__kospi')

    @property
    def kosdaq(self) -> pd.DataFrame:
        if not hasattr(self, '__kosdaq'):
            self.__setattr__('__kosdaq', self.ohlcv(ticker='2001'))
        return self.__getattribute__('__kosdaq')

    @property
    def bank(self) -> pd.DataFrame: # 은행 한정
        if not hasattr(self, '__bank'):
            self.__setattr__('__bank', self.ohlcv(ticker='5046'))
        return self.__getattribute__('__bank')

    @property
    def financial(self) -> pd.DataFrame: # 금융업(은행, 보험, 증권)
        if not hasattr(self, '__financial'):
            self.__setattr__('__financial', self.ohlcv(ticker='5352'))
        return self.__getattribute__('__financial')


if __name__ == "__main__":
    import plotly.graph_objects as go

    pd.set_option('display.expand_frame_repr', False)

    app = data()
    app.period = 90

    print(app.kind)
    print(len(app.deposit(ticker='5352')), app.deposit(ticker='5352'))
    print(app.ohlcv(ticker='5352'))
