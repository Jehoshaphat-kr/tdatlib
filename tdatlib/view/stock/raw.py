from tdatlib import market
from pykrx import stock as krx
import pandas as pd


def getName(ticker:str, namebook=None) -> str:
    if ticker.isalpha():
        name = ticker
    elif len(ticker) == 4:
        name = krx.get_index_ticker_name(ticker=ticker)
    elif len(ticker) == 6:
        if not isinstance(namebook, pd.DataFrame):
            mk = market()
            namebook = pd.concat(objs=[mk.icm, mk.etf_stat], axis=0)
        if not ticker in namebook.index:
            name = krx.get_market_ticker_name(ticker=ticker)
        else:
            name = namebook.loc[ticker, '종목명']
    else:
        raise KeyError(f'{ticker}: Name Not Found')
    return name