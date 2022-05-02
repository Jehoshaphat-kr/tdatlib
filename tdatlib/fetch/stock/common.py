from tdatlib.fetch.archive import root
from datetime import datetime, timedelta
from pytz import timezone
from pykrx import stock
import yfinance as yf
import pandas as pd
import os


def fetch_currency(ticker:str) -> str:
    return 'USD' if ticker.isalpha() else 'KRW' if len(ticker) == 6 else '-'


def fetch_name(ticker:str) -> str:
    if ticker.isalpha():
        return ticker
    elif len(ticker) == 4:
        return stock.get_index_ticker_name(ticker=ticker)
    elif len(ticker) == 6:
        name = stock.get_market_ticker_name(ticker=ticker)
        if isinstance(name, pd.DataFrame):
            return stock.get_etf_ticker_name(ticker=ticker)
        return name


def fetch_ohlcv_raw(ticker:str, period:int=5) -> pd.DataFrame:
    curr = datetime.now(timezone('Asia/Seoul' if ticker.isdigit() else 'US/Eastern'))
    prev = curr - timedelta(365 * period)
    if ticker.isdigit():
        func = stock.get_index_ohlcv_by_date if len(ticker) == 4 else stock.get_market_ohlcv_by_date
        ohlcv = func(fromdate=prev.strftime("%Y%m%d"), todate=curr.strftime("%Y%m%d"), ticker=ticker)
        trade_stop = ohlcv[ohlcv.시가 == 0].copy()
        ohlcv.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop['종가']
    else:
        o_names = ['Open', 'High', 'Low', 'Close', 'Volume']
        c_names = ['시가', '고가', '저가', '종가', '거래량']
        ohlcv = yf.Ticker(ticker).history(period=f'{period}y')[o_names]
        ohlcv.index.name = '날짜'
        ohlcv = ohlcv.rename(columns=dict(zip(o_names, c_names)))
    return ohlcv


def fetch_related(ticker:str) -> (list, list):
    icm = pd.read_csv(os.path.join(root, f'common/icm.csv'), encoding='utf-8', index_col='종목코드')
    icm.index = icm.index.astype(str).str.zfill(6)

    wics = pd.read_csv(os.path.join(root, f'category/wics.csv'), encoding='utf-8', index_col='종목코드')
    wics.index = wics.index.astype(str).str.zfill(6)

    same_sector = wics[wics['섹터'] == wics.loc[ticker, '섹터']][['종목명', '섹터']].join(icm['시가총액'], how='left')
    sames = same_sector.index.tolist()

    n_curr = sames.index(ticker)
    benchmark = same_sector.iloc[[0, 1, 2, 3, 4] if n_curr < 5 else [0, 1, 2, 3] + [n_curr]].index

    if n_curr < 4:
        similar_idx = [0, 1, 2, 3, 4]
    elif n_curr == len(sames) - 1:
        similar_idx = [0, 1, len(sames)-3, len(sames)-2, len(sames)-1]
    else:
        similar_idx = [0, 1, n_curr-1, n_curr, n_curr+1]
    similar = same_sector.iloc[similar_idx].index
    return benchmark.tolist(), similar.tolist()

if __name__ == "__main__":
    print(fetch_related(ticker='253450'))