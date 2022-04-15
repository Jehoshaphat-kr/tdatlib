import pandas as pd
import time, os
from tdatlib.interface.ohlcv import ohlcv
from tqdm import tqdm
from pytz import timezone
from datetime import datetime, timedelta
from pykrx import stock
from inspect import currentframe as inner


DIR_PERF = f'{os.path.dirname(os.path.dirname(__file__))}/archive/common/perf.csv'
PM_DATE = datetime.now(timezone('Asia/Seoul'))
C_MARKET_OPEN = 900 <= int(PM_DATE.strftime("%H%M")) <= 1530


def fetch_trading_dates(td:str) -> dict:
    """
    1D / 1W / 1M / 3M / 6M / 1Y 거래일 다운로드
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
    rtrn = pd.concat(objs={f'R{k}': round(100 * (p_s.TD0D / p_s[f'TD{k}'] - 1), 2) for k in tds.keys()}, axis=1)
    rtrn.index.name = '종목코드'
    return rtrn[rtrn.index.isin(evens)]

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
    rtrn = pd.concat(objs={f'R{k}': round(100 * (p_s.TD0D / p_s[f'TD{k}'] - 1), 2) for k in tds.keys()}, axis=1)
    rtrn.index.name = '종목코드'
    return rtrn

def fetch_returns(td_raw_tickers:tuple or list) -> pd.DataFrame:
    """
    입력 종목코드 리스트에 해당 하는 기간별 수익률
    :return: 
    """
    td, rtrn, tickers = td_raw_tickers
    add_tickers = [ticker for ticker in tickers if not ticker in rtrn.index]
    if not add_tickers:
        return rtrn[rtrn.index.isin(tickers)]

    process = tqdm(add_tickers)
    for ticker in process:
        process.set_description(f'Fetch Returns - {ticker}')
        while True:
            try:
                rtrn = pd.concat(objs=[rtrn, ohlcv(ticker=ticker, period=2).perf], axis=0, ignore_index=False)
                break
            except ConnectionError as e:
                time.sleep(0.5)
    rtrn.index.name = '종목코드'
    if (PM_DATE == td) and C_MARKET_OPEN:
        return rtrn[rtrn.index.isin(tickers)]

    rtrn['날짜'] = td
    rtrn.to_csv(DIR_PERF, encoding='utf-8', index=True)
    return rtrn[rtrn.index.isin(tickers)].drop(columns=['날짜'])
    
class perf(object):

    def __init__(self, date:str):
        self.td_date = date
        pass

    def __attr__(self, **kwargs):
        if not hasattr(self, f'__{kwargs["name"]}'):
            f = globals()[f'fetch_{kwargs["name"]}']
            self.__setattr__(f'__{kwargs["name"]}', f(kwargs['args']) if 'args' in kwargs.keys() else f())
        return self.__getattribute__(f'__{kwargs["name"]}')

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
        rtrn = pd.read_csv(DIR_PERF, encoding='utf-8', index_col='종목코드')
        rtrn.index = rtrn.index.astype(str).str.zfill(6)
        if not str(rtrn['날짜'][0]) == self.td_date:
            rtrn = pd.concat(objs=[self.stock_returns, self.etf_returns], axis=0, ignore_index=False)
            rtrn = rtrn[~rtrn['R1D'].isna()].copy()
            if (PM_DATE == self.td_date) and C_MARKET_OPEN:
                return rtrn
            rtrn['날짜'] = self.td_date
            rtrn.to_csv(DIR_PERF, encoding='utf-8', index=True)
        return rtrn.drop(columns=['날짜'])

    def returns(self, tickers:list) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=[self.td_date, self.market_returns, tickers])


if __name__ == "__main__":
    tester = perf(date='20220415')

    print(tester.td_date)
    # print(tester.trading_dates)
    # print(tester.even_shares)
    # print(tester.stock_returns)
    # print(tester.etf_returns)
    print(tester.market_returns)
    # print(tester.returns(tickers=['005930', '000660']))