import os, time, tdatlib
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from pykrx import stock as krx


class collector:
    __corp, __etf, __idx, __tickers, __objects = None, None, None, list(), dict()
    __market = pd.DataFrame()
    def __init__(self):
        return

    def covers(self, keywords:list):
        """

        :param keywords: 찾고자 하는 지수/ETF 키워드
        :return:
        """
        return
    # keywords = ['은행', '증권', '배당'] # 찾고자하는 테마/섹터 키워드
    # basis = pd.concat(
    #     objs=[etf_list[etf_list['종목명'].str.contains(key)] for key in keywords],
    #     axis=0, ignore_index=False
    # )

    def set_tickers(self, index=None, tickers=None, period:int=5):
        self.__tickers = list()
        if isinstance(index, list):
            for i in index:
                self.__tickers += krx.get_index_portfolio_deposit_file(ticker=i)
        elif isinstance(tickers, list):
            self.__tickers = tickers
        else:
            depo = self.deposit.copy()
            self.__tickers = depo[depo.index.isin(['1028', '2203'])].index.tolist()

        n_tickers = len(self.__tickers)
        iterable = tqdm(tickers) if self.prog == 'tqdm' else tickers
        for n, t in enumerate(iterable):
            self.__objects[t] = tdatlib.stock(ticker=t, period=period, meta=self.icm)
            if self.prog == 'print' or not self.prog:
                print(f'{round(100 * (n + 1) / n_tickers, 2)}% ({(n + 1)}/{n_tickers}) {t} 수집 중...')

        self.__market = pd.DataFrame(index=self.__tickers).join(self.wi26[['섹터']]).join(self.icm)
        return

    def get_object(self, ticker:str):
        if ticker in self.__objects.keys():
            return self.__objects[ticker]
        else:
            print(f'Object not found: {ticker}')

    def set_frame(self, key:str, val):

        return



if __name__ == "__main__":

    test_tickers = ['005930', '000660', '035720', '137310', '253450', '096770']

    app = collector(progress='tqdm')
    # print(app.wics)
    # print(app.wi26)
    # print(app.icm)
    # print(app.deposit)

    app.set_tickers(tickers=test_tickers)
    print(app.get_object(ticker='005930').ohlcv)