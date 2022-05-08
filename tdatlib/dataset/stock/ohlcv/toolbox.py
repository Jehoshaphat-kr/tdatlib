from datetime import datetime, timedelta
from pytz import timezone
from pykrx import stock
import yfinance as yf
import pandas as pd



def fetch_ohlcv(ticker:str, period:int=5) -> pd.DataFrame:
    curr = datetime.now(timezone('Asia/Seoul' if ticker.isdigit() else 'US/Eastern'))
    prev = curr - timedelta(365 * period)
    if ticker.isdigit():
        func = stock.get_index_ohlcv_by_date if len(ticker) == 4 else stock.get_market_ohlcv_by_date
        ohlcv = func(fromdate=prev.strftime("%Y%m%d"), todate=curr.strftime("%Y%m%d"), ticker=ticker)
        trade_stop = ohlcv[ohlcv.시가 == 0].copy()
        if not trade_stop.empty:
            ohlcv.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop['종가']
    else:
        o_names = ['Open', 'High', 'Low', 'Close', 'Volume']
        c_names = ['시가', '고가', '저가', '종가', '거래량']
        ohlcv = yf.Ticker(ticker).history(period=f'{period}y')[o_names]
        ohlcv.index.name = '날짜'
        ohlcv = ohlcv.rename(columns=dict(zip(o_names, c_names)))
    return ohlcv


def calc_returns(ohlcv:pd.DataFrame, ticker:str) -> pd.DataFrame:
    val, data = ohlcv.종가, dict()
    for label, dt in (('R1D', 1), ('R1W', 5), ('R1M', 21), ('R3M', 63), ('R6M', 126), ('R1Y', 252)):
        data[label] = round(100 * val.pct_change(periods=dt)[-1], 2)
    return pd.DataFrame(data=data, index=[ticker])