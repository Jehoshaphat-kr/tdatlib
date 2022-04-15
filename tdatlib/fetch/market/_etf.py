import pandas as pd
import json, os
import urllib.request as req
from inspect import currentframe as inner


URL_ETF = 'https://finance.naver.com/api/sise/etfItemList.nhn'
DIR_ETF = f'{os.path.dirname(os.path.dirname(__file__))}/archive/category/etf.csv'
DIR_ETFXL = f'{os.path.dirname(os.path.dirname(__file__))}/archive/category/__ETF.xlsx'

def fetch_etf_list() -> pd.DataFrame:
    """
    전체 상장 ETF 리스트: 종목코드 / 종목명 / 종가 / 시가총액
    :return: 
    """
    key_prev, key_curr = ['itemcode', 'itemname', 'nowVal', 'marketSum'], ['종목코드', '종목명', '종가', '시가총액']
    df = pd.DataFrame(json.loads(req.urlopen(URL_ETF).read().decode('cp949'))['result']['etfItemList'])
    df = df[key_prev].rename(columns=dict(zip(key_prev, key_curr)))
    df['시가총액'] = df['시가총액'] * 100000000
    return df.set_index(keys='종목코드')

def check_etf_handler(self) -> bool:
    """
    로컬 수기 관리용 ETF 분류 최신화 현황 여부
    :return:
    """
    curr = fetch_etf_list()
    prev = pd.read_excel(DIR_ETFXL, index_col='종목코드')
    prev.index = prev.index.astype(str).str.zfill(6)
    to_be_delete = prev[~prev.index.isin(curr.index)]
    to_be_update = curr[~curr.index.isin(prev.index)]
    if to_be_delete.empty and to_be_update.empty:
        return True

    for kind, frm in [('삭제', to_be_delete), ('추가', to_be_update)]:
        if not frm.empty:
            print("-" * 70, f"\n▷ ETF 분류 {kind} 필요 항목: {'없음' if frm.empty else '있음'}\n{frm}")
    os.startfile(DIR_ETFXL)
    return False

def convert_etf_xl2csv():
    df = pd.read_excel(DIR_ETFXL, index_col='종목코드')
    df.index = df.index.astype(str).str.zfill(6)
    df.to_csv(DIR_ETF, index=True, encoding='utf-8')
    return

class etf(object):

    def __init__(self):
        pass

    def __attr__(self, **kwargs):
        if not hasattr(self, f'__{kwargs["name"]}'):
            f = globals()[f'fetch_{kwargs["name"]}']
            self.__setattr__(f'__{kwargs["name"]}', f(kwargs['args']) if 'args' in kwargs.keys() else f())
        return self.__getattribute__(f'__{kwargs["name"]}')

    @property
    def etf_list(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name)

    @property
    def etf_group(self) -> pd.DataFrame:
        df = pd.read_csv(DIR_ETF, index_col='종목코드')
        df.index = df.index.astype(str).str.zfill(6)
        return df