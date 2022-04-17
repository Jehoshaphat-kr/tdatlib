from inspect import currentframe as inner
from tdatlib.fetch.stock import fetch_stock
from tdatlib.interface.ohlcv._comm import *

class ohlcv(fetch_stock):

    def __attr__(self, **kwargs):
        if not hasattr(self, f'__{kwargs["name"]}'):
            f = globals()[f'calc_{kwargs["name"]}']
            self.__setattr__(f'__{kwargs["name"]}', f(kwargs['args']) if 'args' in kwargs.keys() else f())
        return self.__getattribute__(f'__{kwargs["name"]}')

    @property
    def ta(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=self.ohlcv)

    @property
    def rr(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=self.ohlcv)

    @property
    def dd(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=self.ohlcv)

    @property
    def sma(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=self.ohlcv)

    @property
    def ema(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=self.ohlcv)

    @property
    def iir(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=self.ohlcv)

    @property
    def perf(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=(self.ticker, self.ohlcv))

    @property
    def cagr(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=(self.ticker, self.ohlcv))

    @property
    def volatility(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=(self.ticker, self.ohlcv))

    @property
    def fiftytwo(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=(self.ticker, self.ohlcv))

    @property
    def avg_trend(self) -> pd.DataFrame:
        if not hasattr(self, 'trend'):
            self.__setattr__('trend', trend(ohlcv=self.ohlcv))
        return self.__getattribute__('trend').avg

    @property
    def bnd_trend(self) -> pd.DataFrame:
        if not hasattr(self, 'trend'):
            self.__setattr__('trend', trend(ohlcv=self.ohlcv))
        return self.__getattribute__('trend').bound

if __name__ == "__main__":
    t_ticker = 'TSLA'

    tester = ohlcv(ticker=t_ticker)
    print(tester.ta)
    print(tester.rr)
    print(tester.dd)
    print(tester.sma)
    print(tester.ema)
    print(tester.iir)
    print(tester.perf)
    print(tester.cagr)
    print(tester.volatility)
    print(tester.fiftytwo)
    print(tester.avg_trend)
    print(tester.bnd_trend)