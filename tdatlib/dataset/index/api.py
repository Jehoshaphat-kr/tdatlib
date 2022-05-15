from tdatlib.dataset.stock.ohlcv import technical
from tdatlib.dataset.index.core import (
    fetch_kind,
    fetch_deposit
)
import pandas as pd


class overall(object):
    def __init__(self, td:str = None):
        self.__td = td
        return

    @property
    def kind(self) -> pd.DataFrame:
        """
        :return:
                          KOSPI                                KOSDAQ               KRX                      테마
            지수         지수명   지수                         지수명  지수      지수명  지수              지수명
        0   1001         코스피   2001                         코스닥  5042     KRX 100  1163    코스피 고배당 50
        1   1002  코스피 대형주   2002                  코스닥 대형주  5043  KRX 자동차  1164  코스피 배당성장 50
        2   1003  코스피 중형주   2003                  코스닥 중형주  5044  KRX 반도체  1165  코스피 우선주 지수
        ...  ...            ...    ...                            ...   ...        ...    ...                 ...
        47   NaN            NaN   2216            코스닥 150 정보기술   NaN        NaN    NaN                 NaN
        48   NaN            NaN   2217            코스닥 150 헬스케어   NaN        NaN    NaN                 NaN
        49   NaN            NaN   2218  코스닥 150 커뮤니케이션서비스   NaN        NaN    NaN                 NaN
        """
        return fetch_kind(td=self.__td)


class sole(technical):
    def __init__(self, ticker:str, period:int=5, endate:str=str()):
        super().__init__(ticker=ticker, period=period, endate=endate)
        return


if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    oa = overall()
    print(oa.kind)