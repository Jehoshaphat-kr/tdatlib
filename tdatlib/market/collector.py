import os, time, tdatlib
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from pykrx import stock as krx


class collector:
    def __init__(self, progress:str=str()):
        self.prog = progress
        self.__corp, self.__etf, self.__tickers, self.__objects = None, None, list(), dict()
        self.__wics, self.__wi26 = pd.DataFrame(), pd.DataFrame()
        self.__depo, self.__icm = pd.DataFrame(), pd.DataFrame()
        self.__market = pd.DataFrame()
        self.archive = os.path.join(tdatlib.get_root(__file__), 'archive')
        self.today = datetime.today().strftime("%Y%m%d")

        if not os.path.isdir(os.path.join(self.archive, f'market/{self.today}')):
            os.makedirs(os.path.join(self.archive, f'market/{self.today}'))
        return

    @property
    def icm(self) -> pd.DataFrame:
        """
        상장일(IPO Date), 시가총액(Market Cap), 그리고 투자배수(Multiples) : PyKrx 제공 분
        ETF의 경우, 시가총액 정보만 유효
        """
        if self.__icm.empty:
            _file = os.path.join(self.archive, f'market/{self.today}/icm.csv')
            if os.path.isfile(_file):
                self.__icm = pd.read_csv(_file, index_col='종목코드')
                self.__icm.index = self.__icm.index.astype(str).str.zfill(6)
            else:
                if not isinstance(self.__corp, tdatlib.corporate):
                    self.__corp = tdatlib.corporate()
                if not isinstance(self.__etf, tdatlib.etf):
                    self.__etf = tdatlib.etf()
                self.__icm = pd.concat(
                    objs=[self.__corp.market_ipo, self.__corp.market_cap, self.__corp.market_fundamentals],
                    axis=1
                )
                self.__icm = self.__icm.append(other=self.__etf.list, ignore_index=False)
                self.__icm.to_csv(_file)
        return self.__icm

    @property
    def wics(self) -> pd.DataFrame:
        """
        WICS 산업 분류
        """
        if self.__wics.empty:
            _file = os.path.join(self.archive, f'market/{self.today}/wics.csv')
            if os.path.isfile(_file):
                self.__wics = pd.read_csv(_file, index_col='종목코드')
                self.__wics.index = self.__wics.index.astype(str).str.zfill(6)
            else:
                if not isinstance(self.__corp, tdatlib.corporate):
                    self.__corp = tdatlib.corporate()
                self.__wics = self.__corp.wics
                self.__wics.to_csv(_file)
        return self.__wics

    @property
    def wi26(self) -> pd.DataFrame:
        """
        WI26 업종 분류
        """
        if self.__wi26.empty:
            _file = os.path.join(self.archive, f'market/{self.today}/wi26.csv')
            if os.path.isfile(_file):
                self.__wi26 = pd.read_csv(_file, index_col='종목코드')
                self.__wi26.index = self.__wi26.index.astype(str).str.zfill(6)
            else:
                if not isinstance(self.__corp, tdatlib.corporate):
                    self.__corp = tdatlib.corporate()
                self.__wi26 = self.__corp.wi26
                self.__wi26.to_csv(_file)
        return self.__wi26

    @property
    def theme(self) -> pd.DataFrame:
        """
        테마 분류
        """
        _file = os.path.join(self.archive, f'market/etf_theme/THEME.csv')
        df = pd.read_csv(_file, index_col='종목코드')
        df.index = df.index.astype(str).str.zfill(6)
        return df

    @property
    def etf(self) -> pd.DataFrame:
        """
        ETF 분류
        """
        if not isinstance(self.__etf, tdatlib.etf):
            self.__etf = tdatlib.etf()

        def is_etf_latest(operator) -> bool:
            prev = pd.read_excel(os.path.join(self.archive, f'market/etf_theme/ETF.xlsx'), index_col='종목코드')
            prev.index = prev.index.astype(str).str.zfill(6)
            curr = operator.list
            to_be_delete = prev[~prev.index.isin(curr.index)]
            to_be_update = curr[~curr.index.isin(prev.index)]
            if to_be_delete.empty and to_be_update.empty:
                return True
            else:
                for kind, frm in [('삭제', to_be_delete), ('추가', to_be_update)]:
                    if not frm.empty:
                        print("-" * 70, f"\n▷ ETF 분류 {kind} 필요 항목: {'없음' if frm.empty else '있음'}")
                        print(frm)
                os.startfile(os.path.join(self.archive, 'market/etf_theme'))
                return False

        if self.prog == 'print' or not self.prog:
            is_etf_latest(self.__etf)
        _file = os.path.join(self.archive, f'market/etf_theme/ETF.csv')
        df = pd.read_csv(_file, index_col='종목코드')
        df.index = df.index.astype(str).str.zfill(6)
        return df

    @property
    def deposit(self) -> pd.DataFrame:
        """
        주요 지수: 코스피200, 코스닥150, 코스피 중형주, 코스피 소형주, 코스닥 중형주 종목
        """
        def update(date:str):
            indices, objs = ['1028', '1003', '1004', '2203', '2003'], list()
            for index in indices:
                tickers = krx.get_index_portfolio_deposit_file(ticker=index)
                df = pd.DataFrame(index=tickers)
                df['지수코드'] = index
                df['지수명'] = krx.get_index_ticker_name(index)
                df['날짜'] = date
                objs.append(df)
            return pd.concat(objs=objs, axis=0)

        if self.__depo.empty:
            _file = os.path.join(self.archive, f'market/deposit.csv')
            self.__depo = pd.read_csv(_file, index_col='종목코드')
            self.__depo.index = self.__depo.index.astype(str).str.zfill(6)
            if datetime.today().weekday() == 3:
                latest_date = str(self.__depo['날짜'].values[0])
                if not latest_date == self.today:
                    self.__depo = update(self.today)
                    self.__depo.index.name = '종목코드'
                    self.__depo.to_csv(_file)
        return self.__depo

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

    app = market(progress='tqdm')
    # print(app.wics)
    # print(app.wi26)
    # print(app.icm)
    # print(app.deposit)

    app.set_tickers(tickers=test_tickers)
    print(app.get_object(ticker='005930').ohlcv)