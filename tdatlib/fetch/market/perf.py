from pykrx.stock import (
    get_nearest_business_day_in_a_week,
    get_market_cap_by_ticker,
    get_market_ohlcv_by_ticker,
    get_etf_ohlcv_by_ticker
)
from tdatlib.interface.stock import interface_stock
from tqdm import tqdm
from pytz import timezone
from datetime import datetime, timedelta
import pandas as pd
import time, os


DIR_PERF = f'{os.path.dirname(os.path.dirname(__file__))}/archive/common/perf.csv'
PM_DATE = datetime.now(timezone('Asia/Seoul'))
C_MARKET_OPEN = 900 <= int(PM_DATE.strftime("%H%M")) <= 1530


def __fetch_trading_dates(td:str) -> dict:
    base = {'0D': td}
    td = datetime.strptime(td, "%Y%m%d")
    dm = lambda x: (td - timedelta(x)).strftime("%Y%m%d")
    iter = [('1D', 1), ('1W', 7), ('1M', 30), ('3M', 91), ('6M', 183), ('1Y', 365)]
    base.update({l: get_nearest_business_day_in_a_week(date=dm(d)) for l, d in iter})
    return base


def __fetch_stock_returns(tds:dict) -> pd.DataFrame:
    shares = pd.concat(objs={
        'prev': get_market_cap_by_ticker(date=tds['1Y'], market='ALL')['상장주식수'],
        'curr': get_market_cap_by_ticker(date=tds['0D'], market='ALL')['상장주식수']
    }, axis=1)
    even = shares[shares.prev == shares.curr].index.tolist()

    objs = {f'TD{k}': get_market_ohlcv_by_ticker(date=date, market='ALL', prev=False)['종가']
            for k, date, in tqdm(tds.items(), desc='기간별 수익률 계산(주식)')}
    p_s = pd.concat(objs=objs, axis=1)
    rtrn = pd.concat(objs={f'R{k}': round(100 * (p_s.TD0D / p_s[f'TD{k}'] - 1), 2) for k in tds.keys()}, axis=1)
    rtrn.index.name = '종목코드'
    return rtrn[rtrn.index.isin(even)].drop(columns=['R0D'])


def __fetch_etf_returns(tds:dict) -> pd.DataFrame:
    objs = {f'TD{k}': get_etf_ohlcv_by_ticker(date=date)['종가']
            for k, date in tqdm(tds.items(), desc='기간별 수익률 계산(ETF)')}
    p_s = pd.concat(objs=objs, axis=1)
    rtrn = pd.concat(objs={f'R{k}': round(100 * (p_s.TD0D / p_s[f'TD{k}'] - 1), 2) for k in tds.keys()}, axis=1)
    rtrn.index.name = '종목코드'
    return rtrn[~rtrn['R1D'].isna()].drop(columns=['R0D'])


def __fetch_raw_performance(td:str) -> pd.DataFrame:
    performance = pd.read_csv(DIR_PERF, encoding='utf-8', index_col='종목코드')
    performance.index = performance.index.astype(str).str.zfill(6)
    if str(performance['날짜'][0]) == td:
        return performance.drop(columns=['날짜'])

    tds = __fetch_trading_dates(td=td)
    performance = pd.concat(objs=[__fetch_stock_returns(tds=tds), __fetch_etf_returns(tds=tds)], axis=0)
    if (PM_DATE == td) and C_MARKET_OPEN:
        return performance

    performance['날짜'] = td
    performance.to_csv(DIR_PERF, encoding='utf-8', index=True)
    return performance.drop(columns=['날짜'])


def fetch_performance(td:str, tickers:list) -> pd.DataFrame:
    raw = __fetch_raw_performance(td=td)
    add_tickers = [ticker for ticker in tickers if not ticker in raw.index]
    if not add_tickers:
        return raw[raw.index.isin(tickers)]

    process = tqdm(add_tickers)
    for ticker in process:
        process.set_description(f'Fetch Returns - {ticker}')
        while True:
            # noinspection PyBroadException
            try:
                raw = pd.concat(objs=[raw, interface_stock(ticker=ticker, period=2).perf], axis=0, ignore_index=False)
                break
            except ConnectionError as e:
                time.sleep(0.5)

    raw.index.name = '종목코드'
    if (PM_DATE.strftime("%Y%m%d") == td) and C_MARKET_OPEN:
        return raw[raw.index.isin(tickers)]

    raw['날짜'] = td
    raw.to_csv(DIR_PERF, encoding='utf-8', index=True)
    return raw[raw.index.isin(tickers)].drop(columns=['날짜'])


if __name__ == "__main__":
    print(fetch_performance(td='20220415', tickers=['005960', '005930', '253450']))
