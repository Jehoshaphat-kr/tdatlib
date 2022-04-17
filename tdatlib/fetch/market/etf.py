import pandas as pd
import json, os
import urllib.request as req


URL_ETF = 'https://finance.naver.com/api/sise/etfItemList.nhn'
DIR_ETF = f'{os.path.dirname(os.path.dirname(__file__))}/archive/category/etf.csv'
DIR_ETFXL = f'{os.path.dirname(os.path.dirname(__file__))}/archive/category/__ETF.xlsx'


def fetch_etf_list() -> pd.DataFrame:
    key_prev, key_curr = ['itemcode', 'itemname', 'nowVal', 'marketSum'], ['종목코드', '종목명', '종가', '시가총액']
    df = pd.DataFrame(json.loads(req.urlopen(URL_ETF).read().decode('cp949'))['result']['etfItemList'])
    df = df[key_prev].rename(columns=dict(zip(key_prev, key_curr)))
    df['시가총액'] = df['시가총액'] * 100000000
    return df.set_index(keys='종목코드')


def fetch_etf_group(self) -> pd.DataFrame:
    df = pd.read_csv(DIR_ETF, index_col='종목코드')
    df.index = df.index.astype(str).str.zfill(6)
    return df


def check_etf_handler() -> bool:
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