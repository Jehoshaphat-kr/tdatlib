from tdatlib.dataset.stock.ohlcv import technical
from tdatlib.dataset.stock.fnguide import (
fetch_summary,
fetch_products,

)
from inspect import currentframe as inner


class KR(technical):
    def __init__(self, ticker:str, period:int=5, endate:str=str()):
        super().__init__(ticker=ticker, period=period, endate=endate)
        return

    def __load__(self, p:str, fname:str=str(), **kwargs):
        if not hasattr(self, f'__{p}'):
            try:
                self.__setattr__(f'__{p}', globals()[f"{fname if fname else 'calc'}_{p}"](**kwargs))
            except:
                self.__setattr__(f'__{p}', None)
        return self.__getattribute__(f'__{p}')

    @property
    def summary(self) -> str:
        return self.__load__(inner().f_code.co_name, fname='fetch', ticker=self.ticker)


class US(technical):
    def __init__(self, ticker:str, period:int=5, endate:str=str()):
        super().__init__(ticker=ticker, period=period, endate=endate)
        return