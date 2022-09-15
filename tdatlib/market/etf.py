import pandas as pd
import json, os
import urllib.request as req


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
URL_ETF = 'https://finance.naver.com/api/sise/etfItemList.nhn'
DIR_ETF = f'{ROOT}/_archive/category/etf.csv'


def fetch_etf_list() -> pd.DataFrame:
    key_prev, key_curr = ['itemcode', 'itemname', 'nowVal', 'marketSum'], ['종목코드', '종목명', '종가', '시가총액']
    df = pd.DataFrame(json.loads(req.urlopen(URL_ETF).read().decode('cp949'))['result']['etfItemList'])
    df = df[key_prev].rename(columns=dict(zip(key_prev, key_curr)))
    df['시가총액'] = df['시가총액'] * 100000000
    return df.set_index(keys='종목코드')


def read_etf_group() -> pd.DataFrame:
    df = pd.read_csv(DIR_ETF, index_col='종목코드')
    df.index = df.index.astype(str).str.zfill(6)
    return df

def isetfokay(curr:pd.DataFrame=None) -> bool:
    curr = fetch_etf_list() if curr.empty else curr
    prev = pd.read_csv(DIR_ETF, index_col='종목코드', encoding='utf-8')
    prev.index = prev.index.astype(str).str.zfill(6)
    to_be_delete = prev[~prev.index.isin(curr.index)]
    to_be_update = curr[~curr.index.isin(prev.index)]
    if to_be_delete.empty and to_be_update.empty:
        return True

    for kind, frm in [('삭제', to_be_delete), ('추가', to_be_update)]:
        if not frm.empty:
            print("-" * 70, f"\n▷ ETF 분류 {kind} 필요 항목: {'없음' if frm.empty else '있음'}\n{frm}")
    os.startfile(os.path.dirname(DIR_ETF))
    return False