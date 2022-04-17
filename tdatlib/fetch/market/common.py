from pykrx.stock import (
    get_market_cap_by_ticker,
    get_market_fundamental,
    get_index_portfolio_deposit_file
)
from pytz import timezone
from datetime import datetime
import pandas as pd
import os


URL_KIND = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
DIR_ICM = f'{os.path.dirname(os.path.dirname(__file__))}/archive/common/icm.csv'
DIR_THM = f'{os.path.dirname(os.path.dirname(__file__))}/archive/category/theme.csv'
PM_DATE = datetime.now(timezone('Asia/Seoul'))
C_MARKET_OPEN = 900 <= int(PM_DATE.strftime("%H%M")) <= 1530


def _ipo_() -> pd.DataFrame:
    ipo = pd.read_html(io=URL_KIND, header=0)[0][['회사명', '종목코드', '상장일']]
    ipo = ipo.rename(columns={'회사명': '종목명', '상장일': 'IPO'}).set_index(keys='종목코드')
    ipo.index = ipo.index.astype(str).str.zfill(6)
    ipo.IPO = pd.to_datetime(ipo.IPO)
    return ipo


def _cap_(td:str) -> pd.DataFrame:
    return get_market_cap_by_ticker(date=td, market="ALL", prev=True)


def _mul_(td:str) -> pd.DataFrame:
    return get_market_fundamental(date=td, market="ALL", prev=True)


def fetch_icm(td:str) -> pd.DataFrame:
    icm = pd.read_csv(DIR_ICM, index_col='종목코드', encoding='utf-8')
    icm.index = icm.index.astype(str).str.zfill(6)
    if str(icm['날짜'][0]) == td or (PM_DATE == td and C_MARKET_OPEN):
        return icm.drop(columns=['날짜'])

    icm = pd.concat(objs=[_ipo_(), _cap_(td=td), _mul_(td=td)], axis=1)
    icm['날짜'] = td
    icm.index.name = '종목코드'
    icm.to_csv(DIR_ICM, index=True, encoding='utf-8')
    return icm.drop(columns=['날짜'])


def fetch_theme() -> pd.DataFrame:
    df = pd.read_csv(DIR_THM, index_col='종목코드')
    df.index = df.index.astype(str).str.zfill(6)
    return df

def fetch_kosdaq() -> list:
    return get_index_portfolio_deposit_file('2001')


if __name__ == "__main__":
    print(fetch_icm(td='20220415'))