import pandas as pd
import requests, time, json, os
import urllib.request as req
from tdatlib import archive
from tdatlib.fetch.ohlcv import ohlcv
from tqdm import tqdm
from pytz import timezone
from datetime import datetime, timedelta
from pykrx import stock


class perf:

    def __init__(self):
        pass
    # def __init__(self):
    #     self.krdate = datetime.now(timezone('Asia/Seoul'))
    #     self.tddate = stock.get_nearest_business_day_in_a_week(date=self.krdate.strftime("%Y%m%d"))
    #     return

    def __fetch_trading_dates(self) -> dict:
        """ 1D/1W/1M/3M/6M/1Y 거래일 다운로드 """
        td = datetime.strptime(self.tddate, "%Y%m%d")
        dm = lambda x: (td - timedelta(x)).strftime("%Y%m%d")
        iter = [('1D', 1), ('1W', 7), ('1M', 30), ('3M', 91), ('6M', 183), ('1Y', 365)]
        return {l: stock.get_nearest_business_day_in_a_week(date=dm(d)) for l, d in iter}

    def __fetch_even_shares(self) -> list:
        """ 1Y 대비 상장주식수 미변동 종목 다운로드 """
        if not hasattr(self, 'trading_dates'):
            self.__setattr__('trading_dates', self.__fetch_trading_dates())
        dates = self.__getattribute__('trading_dates')

        shares = pd.concat(objs={
            'prev': stock.get_market_cap_by_ticker(date=dates['1Y'], market='ALL')['상장주식수'],
            'curr': stock.get_market_cap_by_ticker(date=self.tddate, market='ALL')['상장주식수']
        }, axis=1)
        return shares[shares.prev == shares.curr].index.tolist()

    @staticmethod
    def _get_theme() -> pd.DataFrame:
        """ 수기 분류 테마 데이터 읽기 """
        df = pd.read_csv(archive.theme, index_col='종목코드')
        df.index = df.index.astype(str).str.zfill(6)
        return df

    @staticmethod
    def _get_etf_group() -> pd.DataFrame:
        """ 수기 분류 ETF 데이터 읽기 """
        df = pd.read_csv(archive.etf, index_col='종목코드')
        df.index = df.index.astype(str).str.zfill(6)
        return df

    @staticmethod
    def _get_etfs() -> pd.DataFrame:
        """ 전체 상장 ETF 다운로드: 종목코드, 종목명, 종가, 시가총액 """
        url = 'https://finance.naver.com/api/sise/etfItemList.nhn'
        key_prev, key_curr = ['itemcode', 'itemname', 'nowVal', 'marketSum'], ['종목코드', '종목명', '종가', '시가총액']
        df = pd.DataFrame(json.loads(req.urlopen(url).read().decode('cp949'))['result']['etfItemList'])
        df = df[key_prev].rename(columns=dict(zip(key_prev, key_curr)))
        df['시가총액'] = df['시가총액'] * 100000000
        return df.set_index(keys='종목코드')

    def _get_raw_perf(self) -> pd.DataFrame:
        """ 1Y 대비 상장 주식 수 미변동 종목 수익률 산출/저장 """
        filename = archive.perf(self.tddate)
        if os.path.isfile(filename):
            perf = pd.read_csv(filename, encoding='utf-8', index_col='종목코드')
            perf.index = perf.index.astype(str).str.zfill(6)
            return perf

        key = '종가'
        if not hasattr(self, 'even_shares'):
            self.__setattr__('even_shares', self.__fetch_even_shares())
        tds, even_tickers = self.__getattribute__('trading_dates'), self.__getattribute__('even_shares')

        objs = {'TD0D': stock.get_market_ohlcv_by_ticker(date=self.tddate, market='ALL', prev=False)[key]}
        for k, date, in tqdm(tds.items(), desc='기간별 수익률 계산(주식)'):
            objs[f'TD{k}'] = stock.get_market_ohlcv_by_ticker(date=date, market='ALL', prev=False)[key]
        p_s = pd.concat(objs=objs, axis=1)
        perf = pd.concat(objs={f'R{k}': round(100 * (p_s.TD0D / p_s[f'TD{k}'] - 1), 2) for k in tds.keys()}, axis=1)
        perf.index.name = '종목코드'
        corp = perf[perf.index.isin(even_tickers)].copy()

        objs = {'TD0D': stock.get_etf_ohlcv_by_ticker(date=self.tddate)[key]}
        for k, date in tqdm(tds.items(), desc='기간별 수익률 계산(ETF)'):
            objs[f'TD{k}'] = stock.get_etf_ohlcv_by_ticker(date=date)[key]
        p_s = pd.concat(objs=objs, axis=1)
        etf = pd.concat(objs={f'R{k}': round(100 * (p_s.TD0D / p_s[f'TD{k}'] - 1), 2) for k in tds.keys()}, axis=1)
        etf.index.name = '종목코드'

        perf = pd.concat(objs=[corp, etf], axis=0, ignore_index=False)
        perf = perf[~perf['R1D'].isna()].copy()
        perf.to_csv(filename, encoding='utf-8', index=True)
        return perf

    def _get_indices(self) -> pd.DataFrame:
        """ 한국거래소 산업지표 지수 종류 (디스플레이 용) """
        objs = []
        for market in ['KOSPI', 'KOSDAQ', 'KRX', 'THEME']:
            tickers = stock.get_index_ticker_list(market='테마' if market == 'THEME' else market)
            data = pd.DataFrame(data={
                '종목코드': tickers,
                '종목명': [stock.get_index_ticker_name(ticker) for ticker in tickers],
                '지수분류': [market] * len(tickers)
            }).set_index(keys='종목코드')
            obj = data.rename(columns={'종목명': f'{market}지수'}).drop(columns=['지수분류'])
            obj.index.name = f'{market}코드'
            objs.append(obj.reset_index(level=0))
        disp = pd.concat(objs=objs, axis=1).fillna('-')
        return disp

    def etf_check(self) -> bool:
        """ 로컬 수기 관리용 ETF 분류 최신화 현황 여부 """
        curr = self._get_etfs().copy()
        prev = pd.read_excel(archive.etf_xl, index_col='종목코드')
        prev.index = prev.index.astype(str).str.zfill(6)
        to_be_delete = prev[~prev.index.isin(curr.index)]
        to_be_update = curr[~curr.index.isin(prev.index)]
        if to_be_delete.empty and to_be_update.empty:
            return True
        else:
            for kind, frm in [('삭제', to_be_delete), ('추가', to_be_update)]:
                if not frm.empty:
                    print("-" * 70, f"\n▷ ETF 분류 {kind} 필요 항목: {'없음' if frm.empty else '있음'}")
                    print(frm)
            os.startfile(archive.etf_xl)
            return False

    @staticmethod
    def etf_excel2csv():
        """ 수기 관리 ETF 분류 Excel -> CSV변환 """
        df = pd.read_excel(archive.etf_xl, index_col='종목코드')
        df.index = df.index.astype(str).str.zfill(6)
        df.to_csv(archive.etf, index=True, encoding='utf-8')
        return

    def update_perf(self, tickers) -> pd.DataFrame:
        """ 종목 기간별 수익률 업데이트 """
        perf = self._get_raw_perf().copy()
        add_tickers = [ticker for ticker in tickers if not ticker in perf.index]
        if add_tickers:
            process = tqdm(add_tickers)
            for n, ticker in enumerate(process):
                process.set_description(f'Fetch Returns - {ticker}')
                done = False
                while not done:
                    try:
                        other = ohlcv(ticker=ticker, period=2).perf
                        perf = pd.concat(objs=[perf, other], axis=0, ignore_index=False)
                        done = True
                    except ConnectionError as e:
                        time.sleep(0.5)
            perf.index.name = '종목코드'
            perf.to_csv(archive.perf(self.tddate), encoding='utf-8', index=True)
        return perf[perf.index.isin(tickers)]
