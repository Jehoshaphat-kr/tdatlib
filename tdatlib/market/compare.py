import tdatlib
import pandas as pd


class comp:
    __price = pd.DataFrame()
    def __init__(self, tickers:list):
        self.tickers = tickers
        self.objects = {ticker:tdatlib.stock(ticker=ticker, period=5) for ticker in tickers}
        return

    def price(self) -> pd.DataFrame:
        if self.__price.empty:
            objs = {('종가', obj.name):obj.ohlcv['종가'] for obj in self.objects.values()}
            self.__price = pd.concat(objs=objs, axis=1)
        return self.__price




if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    etf = tdatlib.etf()
    etf_list = etf.list

    # keywords = ['은행', '증권', '배당'] # 찾고자하는 테마/섹터 키워드
    # basis = pd.concat(
    #     objs=[etf_list[etf_list['종목명'].str.contains(key)] for key in keywords],
    #     axis=0, ignore_index=False
    # )
    # print(basis)

    # 지수/ETF 종목코드
    i_tickers = ['091220', '157500', '161510', '211900', '281990']
    # i_tickers = ['091170', '102970']
    deposit = pd.concat(
        objs=[etf.deposit(ticker=i_ticker) for i_ticker in i_tickers],
        axis=0, ignore_index=False
    ).drop_duplicates()
    print(deposit)

