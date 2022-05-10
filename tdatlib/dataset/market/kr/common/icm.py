from pykrx.stock import (
    get_market_cap_by_ticker,
    get_market_fundamental,
)
from datetime import datetime
import pandas as pd
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
URL_KRX = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
DIR_ICM = f'{ROOT}/_archive/common/icm.csv'


def __fetchMarketCap(trading_date:str) -> pd.DataFrame:
    return get_market_cap_by_ticker(date=trading_date, market="ALL", prev=True)


def __fetchMultiples(trading_date:str) -> pd.DataFrame:
    return get_market_fundamental(date=trading_date, market="ALL", prev=True)


def __fetchIPO(trading_date:str) -> pd.DataFrame:
    ipo = pd.read_html(io=URL_KRX, header=0)[0][['회사명', '종목코드', '상장일']]
    ipo = ipo.rename(columns={'회사명': '종목명', '상장일': 'IPO'}).set_index(keys='종목코드')
    ipo.index = ipo.index.astype(str).str.zfill(6)
    ipo.IPO = pd.to_datetime(ipo.IPO)
    return ipo[ipo.IPO <= datetime.strptime(trading_date, "%Y%m%d")]


def calc_icm(trading_date:str, is_market_open:bool, write_ok:bool) -> pd.DataFrame:
    icm = pd.read_csv(DIR_ICM, index_col='종목코드', encoding='utf-8')
    icm.index = icm.index.astype(str).str.zfill(6)
    if str(icm['날짜'][0]) == trading_date or is_market_open:
        return icm.drop(columns=['날짜'])

    icm = pd.concat(
        objs=[__fetchIPO(trading_date), __fetchMarketCap(trading_date), __fetchMultiples(trading_date)],
        axis=1
    )
    icm['날짜'] = trading_date
    icm.index.name = '종목코드'
    if write_ok:
        icm.to_csv(DIR_ICM, index=True, encoding='utf-8')
    return icm.drop(columns=['날짜'])