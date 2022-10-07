from pandas_datareader import get_data_fred
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import inspect


class _fetch(object):

    __today  = datetime.now(timezone('Asia/Seoul')).date()
    __period = 20

    @property
    def period(self) -> int:
        return self.__period

    @period.setter
    def period(self, period:int):
        self.__period = period
        return

    def load(self, symbol:str) -> pd.Series:
        """
        Fetch src from Federal Reserve Economic Data | FRED | St. Louis Fed
        :param symbol : symbol
        :return:
        """
        if not hasattr(self, f'__{symbol}{self.__period}'):
            start, end = self.__today - timedelta(self.__period * 365), self.__today
            fetch = get_data_fred(symbols=symbol, start=start, end=end)
            self.__setattr__(
                f'__{symbol}{self.__period}',
                pd.Series(
                    name=symbol, dtype=float,
                    index=fetch.index, data=fetch[symbol]
                )
            )
        return self.__getattribute__(f'__{symbol}{self.__period}')


class fred(_fetch):

    @property
    def props(self) -> list:
        return [e for e in self.__dir__() if not e.startswith('_') and not (e[0].isalpha() and e[0].islower())]

    @property
    def 기준금리(self) -> pd.Series:
        return self.load('DFF')

    @property
    def 국고채2Y(self) -> pd.Series:
        return self.load('DGS2')

    @property
    def 국고채3Y(self) -> pd.Series:
        return self.load('DGS3MO')

    @property
    def 국고채10Y(self) -> pd.Series:
        return self.load('DGS10')

    @property
    def 국고채10Y인플레이션반영(self) -> pd.Series:
        return self.load('DFII10')

    @property
    def 장단기금리차10Y3M(self) -> pd.Series:
        return self.load('T10Y3M')

    @property
    def 장단기금리차10Y2Y(self) -> pd.Series:
        return self.load('T10Y2Y')

    @property
    def 하이일드스프레드(self) -> pd.Series:
        return self.load('BAMLH0A0HYM2')

    @property
    def 기대인플레이션5Y(self) -> pd.Series:
        return self.load('T5YIE')

    @property
    def 기대인플레이션10Y(self) -> pd.Series:
        return self.load('T10YIE')

    @property
    def CPI(self) -> pd.Series:
        return self.load('CPIAUCSL')

    @property
    def BRENT유(self) -> pd.Series:
        return self.load('DCOILBRENTEU')

    @property
    def WTI유(self) -> pd.Series:
        return self.load('DCOILWTICO')


if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    app = fred()
    app.period = 15

    print(app.props)
    print(app.기준금리)