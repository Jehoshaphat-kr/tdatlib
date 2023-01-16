from pykrx.stock import (
    get_index_ticker_list,
    get_index_ticker_name,
    get_index_portfolio_deposit_file
)
import pandas as pd


def fetch_kind(td:str = None) -> pd.DataFrame:
    objs = dict()
    for market in ('KOSPI', 'KOSDAQ', 'KRX', '테마'):
        indices = get_index_ticker_list(date=td, market=market)
        names = [get_index_ticker_name(index) for index in indices]
        objs[market] = pd.DataFrame(data={'지수': indices, '지수명': names})
    return pd.concat(objs=objs, axis=1)


def fetch_deposit(ticker:str, td:str = None) -> list:
    return get_index_portfolio_deposit_file(ticker, date=td)


if __name__ == "__main__":
    df = fetch_list()
    print(df)
