from datetime import datetime, timedelta
from pytz import timezone
from pykrx import stock
import yfinance as yf
import pandas as pd


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


def fetch_ohlcv(ticker:str, period:int=5) -> pd.DataFrame:
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


def fetch_related(ticker:str) -> list:
    return list()