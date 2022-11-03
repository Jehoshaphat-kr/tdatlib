from pykrx.stock import (
    get_market_cap_by_ticker,
    get_market_fundamental,
    get_market_ohlcv_by_ticker,
    get_market_ohlcv_by_date
)
from tqdm import tqdm
from datetime import datetime, timedelta
import pandas as pd
import requests, time, os


class marketime(object):
    def __init__(self, td:str or datetime=None):
        clk = datetime.now(timezone('Asia/Seoul'))
        cur = get_nearest_business_day_in_a_week(date=clk.strftime("%Y%m%d"), prev=True)

        if td and isinstance(td, str):
            date = td
        elif td and isinstance(td, datetime):
            date = td.strftime("%Y%m%d")
        else:
            date = datetime.now(timezone('Asia/Seoul')).strftime("%Y%m%d")

        self.recent = get_nearest_business_day_in_a_week(date=date, prev=True)
        self.is_open = True if self.recent == cur and 900 <= int(clk.strftime("%H%M")) <= 1530 else False
        return

    @property
    def dates(self) -> dict:
        if not hasattr(self, '__dates'):
            base = {'0D': self.recent}
            td = datetime.strptime(self.recent, "%Y%m%d")
            dm = lambda x: (td - timedelta(x)).strftime("%Y%m%d")
            loop = [('1D', 1), ('1W', 7), ('1M', 30), ('3M', 91), ('6M', 183), ('1Y', 365)]
            base.update({l: get_nearest_business_day_in_a_week(date=dm(d)) for l, d in loop})
            self.__setattr__('__dates', base)
        return self.__getattribute__('__dates')

    @property
    def wdate(self) -> str:
        if not hasattr(self, f'__wdate'):
            src = requests.get(url='http://www.wiseindex.com/Index/Index#/G1010.0.Components').text
            tic = src.find("기준일")
            toc = tic + src[tic:].find("</p>")
            self.__setattr__(f'__wdate', src[tic + 6: toc].replace('.', ''))
        return self.__getattribute__(f'__wdate')



class _group(marketime):
    _dir = os.path.join(os.path.dirname(__file__), rf'archive/category')
    _labels = {
        'WICS': {
            'G1010': '에너지',
            'G1510': '소재',
            'G2010': '자본재',
            'G2020': '상업서비스와공급품',
            'G2030': '운송',
            'G2510': '자동차와부품',
            'G2520': '내구소비재와의류',
            'G2530': '호텔,레스토랑,레저 등',
            'G2550': '소매(유통)',
            'G2560': '교육서비스',
            'G3010': '식품과기본식료품소매',
            'G3020': '식품,음료,담배',
            'G3030': '가정용품과개인용품',
            'G3510': '건강관리장비와서비스',
            'G3520': '제약과생물공학',
            'G4010': '은행',
            'G4020': '증권',
            'G4030': '다각화된금융',
            'G4040': '보험',
            'G4050': '부동산',
            'G4510': '소프트웨어와서비스',
            'G4520': '기술하드웨어와장비',
            'G4530': '반도체와반도체장비',
            'G4535': '전자와 전기제품',
            'G4540': '디스플레이',
            'G5010': '전기통신서비스',
            'G5020': '미디어와엔터테인먼트',
            'G5510': '유틸리티'
        },
        'WI26' : {
            'WI100': '에너지',
            'WI110': '화학',
            'WI200': '비철금속',
            'WI210': '철강',
            'WI220': '건설',
            'WI230': '기계',
            'WI240': '조선',
            'WI250': '상사,자본재',
            'WI260': '운송',
            'WI300': '자동차',
            'WI310': '화장품,의류',
            'WI320': '호텔,레저',
            'WI330': '미디어,교육',
            'WI340': '소매(유통)',
            'WI400': '필수소비재',
            'WI410': '건강관리',
            'WI500': '은행',
            'WI510': '증권',
            'WI520': '보험',
            'WI600': '소프트웨어',
            'WI610': 'IT하드웨어',
            'WI620': '반도체',
            'WI630': 'IT가전',
            'WI640': '디스플레이',
            'WI700': '통신서비스',
            'WI800': '유틸리티',
        }
    }
    _wise_url = 'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt=%s&sec_cd=%s'

    def _fetch(self, name:str) -> pd.DataFrame:
        loop, data = tqdm(self._labels[name].items()), list()
        for c, l in loop:
            loop.set_description(desc=f'{name} / {l}({c}) ...')
            for n in range(6):
                req = requests.get(self._wise_url % (self.wdate, c))
                if req.status_code == 200:
                    for _ in req.json()['list']:
                        data.append([_['CMP_CD'], _['CMP_KOR'], _['SEC_NM_KOR'], _['IDX_NM_KOR'][5:], self.wdate])
                    break
                print(
                    f"\t- Failed fetching WISE category {name} / {l}({c})" if n == 5 else \
                    f"\t- HTTP Error while fetching WISE category {name} / {l}({c})... redirecting... ({n + 1})"
                )
                if n < 5:
                    time.sleep(5)
        return pd.DataFrame(data=data, columns=['종목코드', '종목명', '산업', '섹터', '날짜']).set_index(keys='종목코드')

    @property
    def wics(self) -> pd.DataFrame:
        if not hasattr(self, f'__wics'):
            fetch = pd.read_csv(os.path.join(self._dir, 'wics.csv'), index_col='종목코드', encoding='utf-8')
            fetch.index = fetch.index.astype(str).str.zfill(6)
            if not str(fetch['날짜'][0]) == self.wdate:
                fetch = self._fetch(name='WICS')
                fetch.to_csv(os.path.join(self._dir, 'wics.csv'), index=True, encoding='utf-8')
            self.__setattr__(f'__wics', fetch.drop(columns=['날짜']))
        return self.__getattribute__(f'__wics')

    @property
    def wi26(self) -> pd.DataFrame:
        if not hasattr(self, f'__wi26'):
            fetch = pd.read_csv(os.path.join(self._dir, 'wi26.csv'), index_col='종목코드', encoding='utf-8')
            fetch.index = fetch.index.astype(str).str.zfill(6)
            if not str(fetch['날짜'][0]) == self.wdate:
                fetch = self._fetch(name='WI26')
                fetch.drop(columns=['산업'], inplace=True)
                fetch.to_csv(os.path.join(self._dir, 'wi26.csv'), index=True, encoding='utf-8')
            self.__setattr__(f'__wi26', fetch.drop(columns=['날짜']))
            return self.__getattribute__(f'__wi26')

    @property
    def theme(self) -> pd.DataFrame:
        df = pd.read_csv(os.path.join(self._dir, 'theme.csv'), index_col='종목코드')
        df.index = df.index.astype(str).str.zfill(6)
        return df



class _basis(_group):

    def _get_marketcap(self) -> pd.DataFrame:
        return get_market_cap_by_ticker(date=self.recent, market="ALL", alternative=True)

    def _get_multiples(self) -> pd.DataFrame:
        return get_market_fundamental(date=self.recent, market="ALL", alternative=True)

    def _get_ipo(self) -> pd.DataFrame:
        io = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
        ipo = pd.read_html(io=io, header=0)[0][['회사명', '종목코드', '상장일']]
        ipo = ipo.rename(columns={'회사명': '종목명', '상장일': 'IPO'}).set_index(keys='종목코드')
        ipo.index = ipo.index.astype(str).str.zfill(6)
        ipo.IPO = pd.to_datetime(ipo.IPO)
        return ipo[ipo.IPO <= datetime.strptime(self.recent, "%Y%m%d")]

    def calc_performance(self, ticker: str) -> pd.DataFrame:
        ohlcv = get_market_ohlcv_by_date(ticker=ticker, fromdate=self.dates['1Y'], todate=self.dates['0D'])
        data = {
            label: round(100 * ohlcv.pct_change(periods=dt)[-1], 2)
            for label, dt in [('R1D', 1), ('R1W', 5), ('R1M', 21), ('R3M', 63), ('R6M', 126), ('R1Y', 252)]
        }
        return pd.DataFrame(data=data, index=[ticker])

    @property
    def overview(self) -> pd.DataFrame:
        if not hasattr(self, '__basis'):
            path = os.path.join(os.path.dirname(__file__), rf'archive/common/basis.csv')
            _basis = pd.read_csv(path, index_col='종목코드', encoding='utf-8')
            _basis.index = _basis.index.astype(str).str.zfill(6)
            _basis.IPO = pd.to_datetime(_basis.IPO)
            if not self.is_open and not str(_basis['날짜'][0]) == self.recent:
                _basis = pd.concat(objs = [self._get_ipo(), self._get_marketcap(), self._get_multiples()], axis=1)
                _basis['날짜'] = self.recent
                _basis.index.name = '종목코드'
                _basis.to_csv(path, index=True, encoding='utf-8')
            self.__setattr__('__basis', _basis.drop(columns=['날짜']))
        return self.__getattribute__('__basis')

    @property
    def static_performance(self) -> pd.DataFrame:
        if not hasattr(self, '__static_performance'):
            shares = pd.concat(objs={
                'prev': get_market_cap_by_ticker(date=self.dates['1Y'], market='ALL')['상장주식수'],
                'curr': get_market_cap_by_ticker(date=self.dates['0D'], market='ALL')['상장주식수']
            }, axis=1)
            even = shares[shares.prev == shares.curr].index.tolist()

            prices = pd.concat({
                f'TD{k}': get_market_ohlcv_by_ticker(date=date, market='ALL', alternative=False)['종가']
                for k, date, in tqdm(self.dates.items(), desc='기간별 수익률 계산(주식)')
            }, axis=1)

            rtrn = pd.concat(
                objs={f'R{k}': round(100 * (prices['TD0D'] / prices[f'TD{k}'] - 1), 2) for k in self.dates.keys()},
                axis=1
            )
            rtrn.index.name = '종목코드'
            self.__setattr__('__static_performance', rtrn[rtrn.index.isin(even)].drop(columns=['R0D']))
        return self.__getattribute__('__static_performance')




# class _performance(object):
#
#     def __init__(self, td:str, tdset:dict, market_open:bool=False):
#         self._td, self.dates, self._market_open = td, tdset, market_open
#         return
#

#

#
#     def _stack_performance(self) -> pd.DataFrame:
#
#         return pd.DataFrame()


# ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# DIR_PERF = f'{ROOT}/_archive/common/perf.csv'
# PM_DATE = datetime.now(timezone('Asia/Seoul'))
# C_MARKET_OPEN = 900 <= int(PM_DATE.strftime("%H%M")) <= 1530


# def __fetch_trading_dates(td:str) -> dict:
#     base = {'0D': td}
#     td = datetime.strptime(td, "%Y%m%d")
#     dm = lambda x: (td - timedelta(x)).strftime("%Y%m%d")
#     loop = [('1D', 1), ('1W', 7), ('1M', 30), ('3M', 91), ('6M', 183), ('1Y', 365)]
#     base.update({l: get_nearest_business_day_in_a_week(date=dm(d)) for l, d in loop})
#     return base

# def __fetch_etf_returns(tds:dict) -> pd.DataFrame:
#     objs = {f'TD{k}': get_etf_ohlcv_by_ticker(date=date)['종가']
#             for k, date in tqdm(tds.items(), desc='기간별 수익률 계산(ETF)')}
#     p_s = pd.concat(objs=objs, axis=1)
#     rtrn = pd.concat(objs={f'R{k}': round(100 * (p_s.TD0D / p_s[f'TD{k}'] - 1), 2) for k in tds.keys()}, axis=1)
#     rtrn.index.name = '종목코드'
#     return rtrn[~rtrn['R1D'].isna()].drop(columns=['R0D'])
#
#
# def __fetch_raw_returns(td:str, is_market_open:bool, write_ok:bool) -> pd.DataFrame:
#     performance = pd.read_csv(DIR_PERF, encoding='utf-8', index_col='종목코드')
#     performance.index = performance.index.astype(str).str.zfill(6)
#     if str(performance['날짜'][0]) == td or is_market_open:
#         return performance.drop(columns=['날짜'])
#
#     tds = __fetch_trading_dates(td=td)
#     performance = pd.concat(objs=[__fetch_stock_returns(tds=tds), __fetch_etf_returns(tds=tds)], axis=0)
#     performance['날짜'] = td
#     if write_ok:
#         performance.to_csv(DIR_PERF, encoding='utf-8', index=True)
#     return performance.drop(columns=['날짜'])
#
#
# def fetch_returns(td:str, tickers:list, is_market_open:bool, write_ok:bool) -> pd.DataFrame:
#     raw = __fetch_raw_returns(td=td, is_market_open=is_market_open, write_ok=write_ok)
#     add_tickers = [ticker for ticker in tickers if not ticker in raw.index]
#     if not add_tickers:
#         return raw[raw.index.isin(tickers)]
#
#     process = tqdm(add_tickers)
#     for ticker in process:
#         process.set_description(f'Fetch Returns - {ticker}')
#         while True:
#             # noinspection PyBroadException
#             try:
#                 raw = pd.concat(objs=[raw, technical(ticker=ticker, period=2).ohlcv_returns], axis=0, ignore_index=False)
#                 break
#             except ConnectionError as e:
#                 time.sleep(0.5)
#
#     raw.index.name = '종목코드'
#     if is_market_open:
#         return raw[raw.index.isin(tickers)]
#
#     raw['날짜'] = td
#     if write_ok:
#         raw.to_csv(DIR_PERF, encoding='utf-8', index=True)
#     return raw[raw.index.isin(tickers)].drop(columns=['날짜'])



if __name__ == "__main__":

    # group = _group()
    # print(group.wics)
    # print(group.wi26)
    # print(group.theme)

    from pykrx.stock import get_nearest_business_day_in_a_week
    from pytz import timezone

    _now = datetime.now(timezone('Asia/Seoul'))
    _lat = get_nearest_business_day_in_a_week(date=_now.strftime("%Y%m%d"))
    basis = _basis(td=_lat)
    print(basis.overview)