import pandas as pd
from inspect import currentframe as inner
from tdatlib.fetch.stock import ohlcv as basis
from tdatlib.interface.ohlcv._comm import (
    calc_perf
)

class ohlcv(basis):

    def __attr__(self, **kwargs):
        if not hasattr(self, f'__{kwargs["name"]}'):
            f = globals()[f'calc_{kwargs["name"]}']
            self.__setattr__(f'__{kwargs["name"]}', f(kwargs['args']) if 'args' in kwargs.keys() else f())
        return self.__getattribute__(f'__{kwargs["name"]}')

    @property
    def perf(self) -> pd.DataFrame:
        return self.__attr__(name=inner().f_code.co_name, args=(self.ticker, self.ohlcv))

if __name__ == "__main__":
    t_ticker = '005930'

    tester = ohlcv(ticker=t_ticker)
    print(tester.perf)