from datetime import datetime, timedelta
from pytz import timezone
from pykrx import stock
import yfinance as yf
import pandas as pd


def fetch_ohlcv(ticker:str, period:int=5) -> pd.DataFrame:
    """
    주가 시계열
    :return:
    """
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


if __name__ == "__main__":
    # t_ticker = '005930'
    t_ticker = 'TSLA'

    print(fetch_ohlcv(ticker=t_ticker))