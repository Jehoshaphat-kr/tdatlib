from tdatlib.interface.market.sampling import (
    get_baseline
)
from tdatlib.interface.stock import interface_stock
from tdatlib.fetch.market import fetch_market
from inspect import currentframe as inner
from tqdm import tqdm
import pandas as pd


class interface_market(fetch_market):

    def __gettter__(self, p: str, fname: str = str(), **kwargs):
        if not hasattr(self, f'__{p}'):
            self.__setattr__(f'__{p}', globals()[f"{fname if fname else f'get_{p}'}"](**kwargs))
        return self.__getattribute__(f'__{p}')

    def __iscoll__(self):
        if not hasattr(self, 'is_coll'):
            proc = tqdm(self.target)
            for ticker in proc:
                proc.set_description(desc=f'Collecting object ... {ticker}')
                self.__setattr__(f'__{ticker}', interface_stock(ticker=ticker, period=5))
            self.__setattr__('is_coll', True)
        return self.__getattribute__('is_coll')

    def __reset__(self):
        for ticker in self.target:
            if not hasattr(self, f'__{ticker}'):
                self.__setattr__(f'__{ticker}', interface_stock(ticker=ticker, period=5))
        return

    def set_target(self, category:str):
        if category.lower() == 'kospi':
            self.__setattr__('__target', self.kospi)
        elif category.lower() == 'kosdaq':
            self.__setattr__('__target', self.kosdaq)
        elif category.lower() == 'kospi200':
            self.__setattr__('__target', self.kospi200)
        elif category.lower() == 'kosdaq150':
            self.__setattr__('__target', self.kosdaq150)
        elif category.lower() == 'midcap':
            self.__setattr__('__target', self.kospi_midcap + self.kosdaq_midcap)
        elif category.lower() == 'all':
            self.__setattr__('__target', self.kospi + self.kosdaq)
        else:
            raise KeyError(f'Parameter category = {category} is not the right target')
        self.__delattr__('__baseline')
        return

    def reset_target(self):
        self.__setattr__('__target', self.kospi200 + self.kosdaq150)
        self.__delattr__('__baseline')
        return

    @property
    def target(self) -> list:
        if not hasattr(self, '__target'):
            self.reset_target()
        return self.__getattribute__('__target')

    @property
    def baseline(self) -> pd.DataFrame:
        return self.__gettter__(
            inner().f_code.co_name,
            tickers=self.target,
            wics=self.wics,
            icm=self.icm,
            perf=self.performance(tickers=self.target),
        )


if __name__ == "__main__":
    tester = interface_market()

    print(tester.baseline)