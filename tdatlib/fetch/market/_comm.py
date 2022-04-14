import pandas as pd
import requests, time, json, os
import urllib.request as req
from tdatlib import archive
from tdatlib.fetch.ohlcv import ohlcv
from tqdm import tqdm
from pytz import timezone
from datetime import datetime, timedelta
from pykrx import stock
from inspect import currentframe as inner


DIR_PERF = f'{os.path.dirname(os.path.dirname(__file__))}/archive/common/perf.csv'

def fetch_date() -> str:
    """
    실행 시각 기준, 최근 유효 거래일
    :return: %y%m%d
    """
    return stock.get_nearest_business_day_in_a_week(date=datetime.now(timezone('Asia/Seoul')).strftime("%Y%m%d"))

def fetch_trading_dates(td:str) -> dict:
    """
    1D/1W/1M/3M/6M/1Y 거래일 다운로드
    :return:
    """
    td = datetime.strptime(td, "%Y%m%d")
    dm = lambda x: (td - timedelta(x)).strftime("%Y%m%d")
    iter = [('1D', 1), ('1W', 7), ('1M', 30), ('3M', 91), ('6M', 183), ('1Y', 365)]
    return {l: stock.get_nearest_business_day_in_a_week(date=dm(d)) for l, d in iter}

def fetch_even_shares(dates:tuple or list) -> list:
    """
    1Y 기준 상장주식수 미변동 분 종목코드 리스트
    :return:
    """
    prev, curr = dates
    shares = pd.concat(objs={
        'prev': stock.get_market_cap_by_ticker(date=prev, market='ALL')['상장주식수'],
        'curr': stock.get_market_cap_by_ticker(date=curr, market='ALL')['상장주식수']
    }, axis=1)
    return shares[shares.prev == shares.curr].index.tolist()

def fetch_stock_returns(td_tds_evens:tuple or list) -> pd.DataFrame:
    """
    상장 주식 기간별 수익률
    :return: 
    """
    td, tds, evens = td_tds_evens
    objs = {'TD0D': stock.get_market_ohlcv_by_ticker(date=td, market='ALL', prev=False)['종가']}
    for k, date, in tqdm(tds.items(), desc='기간별 수익률 계산(주식)'):
        objs[f'TD{k}'] = stock.get_market_ohlcv_by_ticker(date=date, market='ALL', prev=False)['종가']
    p_s = pd.concat(objs=objs, axis=1)
    perf = pd.concat(objs={f'R{k}': round(100 * (p_s.TD0D / p_s[f'TD{k}'] - 1), 2) for k in tds.keys()}, axis=1)
    perf.index.name = '종목코드'
    return perf[perf.index.isin(evens)]

def fetch_etf_returns(td_tds:tuple or list) -> pd.DataFrame:
    """
    상장 ETF 기간별 수익률
    :return: 
    """
    td, tds = td_tds
    objs = {'TD0D': stock.get_etf_ohlcv_by_ticker(date=td)['종가']}
    for k, date in tqdm(tds.items(), desc='기간별 수익률 계산(ETF)'):
        objs[f'TD{k}'] = stock.get_etf_ohlcv_by_ticker(date=date)['종가']
    p_s = pd.concat(objs=objs, axis=1)
    perf = pd.concat(objs={f'R{k}': round(100 * (p_s.TD0D / p_s[f'TD{k}'] - 1), 2) for k in tds.keys()}, axis=1)
    perf.index.name = '종목코드'
    return perf
    
class common:

    def __init__(self):
        pass

    def __attr__(self, **kwargs):
        name = kwargs['name']
        keys = kwargs['key'] if 'key' in kwargs.keys() else 'fetch'
        if not hasattr(self, f'__{name}'):
            _func = globals()[f'{keys}_{name}']
            if 'args' in kwargs.keys():
                self.__setattr__(f'__{name}', _func(kwargs['args']))
            else:
                self.__setattr__(f'__{name}', _func())
        return self.__getattribute__(f'__{name}')

    @property
    def td_date(self) -> str:
        return self.__attr__(name=inner().f_code.co_name)

    @property
    def trading_dates(self) -> dict:
        return self.__attr__(name=inner().f_code.co_name, args=self.td_date)

    @property
    def even_shares(self) -> list:
        return self.__attr__(name=inner().f_code.co_name, args=(self.trading_dates['1Y'], self.td_date))

    @property
    def stock_returns(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=[self.td_date, self.trading_dates, self.even_shares])

    @property
    def etf_returns(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=[self.td_date, self.trading_dates])

    @property
    def market_returns(self):
        perf = pd.read_csv(DIR_PERF, encoding='utf-8', index_col='종목코드')
        perf.index = perf.index.astype(str).str.zfill(6)
        if not str(perf['날짜'][0]) == self.td_date:
            return self.market_returns_latest
        return perf.drop(columns=['날짜'])

    @property
    def market_returns_latest(self):
        perf = pd.concat(objs=[self.stock_returns, self.etf_returns], axis=0, ignore_index=False)
        perf = perf[~perf['R1D'].isna()].copy()
        perf['날짜'] = self.td_date
        perf.to_csv(DIR_PERF, encoding='utf-8', index=True)
        return perf.drop(columns=['날짜'])

    def update_returns(self, tickers) -> pd.DataFrame:
        """ 종목 기간별 수익률 업데이트 """
        perf = self.market_returns.copy()
        add_tickers = [ticker for ticker in tickers if not ticker in perf.index]
        if not add_tickers:
            return perf[perf.index.isin(tickers)]

        process = tqdm(add_tickers)
        for n, ticker in enumerate(process):
            process.set_description(f'Fetch Returns - {ticker}')
            while True:
                try:
                    other = ohlcv(ticker=ticker, period=2).perf
                    perf = pd.concat(objs=[perf, other], axis=0, ignore_index=False)
                    break
                except ConnectionError as e:
                    time.sleep(0.5)
        perf.index.name = '종목코드'
        perf.to_csv(archive.perf(self.td_date), encoding='utf-8', index=True)
        return perf[perf.index.isin(tickers)]


if __name__ == "__main__":
    tester = common()

    # print(tester.date)
    # print(tester.trading_dates)
    # print(tester.even_shares)
    # print(tester.stock_returns)
    # print(tester.etf_returns)
    # print(tester.market_returns_latest)
    print(tester.market_returns)