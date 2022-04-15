import pandas as pd
import os
from pytz import timezone
from datetime import datetime
from pykrx import stock
from inspect import currentframe as inner


URL_KIND = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
DIR_ICM = f'{os.path.dirname(os.path.dirname(__file__))}/archive/common/icm.csv'
DIR_THM = f'{os.path.dirname(os.path.dirname(__file__))}/archive/category/theme.csv'
PM_DATE = datetime.now(timezone('Asia/Seoul'))

def fetch_ipo() -> pd.DataFrame:
    """
    상장일 포함 전 종목 데이터 프레임
    :return:
    """
    ipo = pd.read_html(io=URL_KIND, header=0)[0][['회사명', '종목코드', '상장일']]
    ipo = ipo.rename(columns={'회사명': '종목명', '상장일': 'IPO'}).set_index(keys='종목코드')
    ipo.index = ipo.index.astype(str).str.zfill(6)
    ipo.IPO = pd.to_datetime(ipo.IPO)
    return ipo

def fetch_cap() -> pd.DataFrame:
    """
    시가총액 전 종목 데이터 프레임
    :return:
    """
    return stock.get_market_cap_by_ticker(date=PM_DATE.strftime("%Y%m%d"), market="ALL", prev=True)

def fetch_mul() -> pd.DataFrame:
    """
    투자배수 및 (x)ps 전 종목 데이터 프레임
    :return: 
    """
    return stock.get_market_fundamental(date=PM_DATE.strftime("%Y%m%d"), market="ALL", prev=True)

def fetch_icm(ipo_cap_mul:tuple or list) -> pd.DataFrame:
    """
    IPO, (market)Cap 및 Multiple 데이터 프레임
    :return:
    """
    icm = pd.read_csv(DIR_ICM, index_col='종목코드', encoding='utf-8')
    icm.index = icm.index.astype(str).str.zfill(6)
    icm_date = str(icm['날짜'][0])

    td_date = stock.get_nearest_business_day_in_a_week(PM_DATE.strftime("%Y%m%d"))
    is_weekend = PM_DATE.weekday() == 5 or PM_DATE.weekday() == 6
    is_market_open = 855 < int(PM_DATE.strftime("%H%M")) <= 1530
    if is_weekend or is_market_open or icm_date == td_date:
        return icm.drop(columns=['날짜'])

    icm = pd.concat(objs=ipo_cap_mul, axis=1)
    icm['날짜'] = td_date
    icm.index.name = '종목코드'
    icm.to_csv(DIR_ICM, index=True, encoding='utf-8')
    return icm.drop(columns=['날짜'])


class comm(object):

    def __init__(self):
        pass

    def __attr__(self, **kwargs):
        if not hasattr(self, f'__{kwargs["name"]}'):
            f = globals()[f'fetch_{kwargs["name"]}']
            self.__setattr__(f'__{kwargs["name"]}', f(kwargs['args']) if 'args' in kwargs.keys() else f())
        return self.__getattribute__(f'__{kwargs["name"]}')

    @property
    def ipo(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name)

    @property
    def cap(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name)

    @property
    def mul(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name)

    @property
    def icm(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=[self.ipo, self.cap, self.mul])

    @property
    def theme(self) -> pd.DataFrame:
        df = pd.read_csv(DIR_THM, index_col='종목코드')
        df.index = df.index.astype(str).str.zfill(6)
        return df


if __name__ == "__main__":
    tester = common()

    # print(tester.ipo)
    # print(tester.cap)
    # print(tester.mul)
    print(tester.icm)