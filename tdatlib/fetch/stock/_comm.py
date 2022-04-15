from pykrx import stock
import pandas as pd


def fetch_name(ticker:str):
    """
    종목코드/티커에 따른 종목명
    :return:
    """
    if ticker.isalpha():
        return ticker
    elif len(ticker) == 4:
        return stock.get_index_ticker_name(ticker=ticker)
    elif len(ticker) == 6:
        name = stock.get_market_ticker_name(ticker=ticker)
        if isinstance(name, pd.DataFrame):
            return stock.get_etf_ticker_name(ticker=ticker)
        return name

def fetch_related(ticker:str) -> list:
    return list()


class comm(object):

    def __init__(self, ticker:str, name:str=str()):
        self.ticker, self.__name = ticker, name
        return

    @property
    def name(self):
        if not self.__name:
            self.__name = fetch_name(ticker=self.ticker)
        return self.__name


if __name__ == "__main__":
    # t_ticker = 'TSLA'
    t_ticker = '005930'

    tester = comm(ticker=t_ticker)

    print(tester.name)