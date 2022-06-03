from tdatlib.dataset.market.kr.api import KR as _market
from tdatlib.viewer.stock import KR as _stock
from scipy import stats
import pandas as pd
import numpy as np


"""
# REFERENCE ATTRIBUTE SETTER
def attr(obj:object, target:list):
    attribs = list()
    proc = tqdm(target)
    for ticker in proc:
        proc.set_description(desc=f'Set Attribute ... {ticker}')
        attr = getattr(obj, f'A{ticker}')

        # This is where you put external attributs
        attribs.append(attr.ta.volume_mfi[-1])
    return pd.Series(data=attribs, index=target, name='pt_mfi')
"""

CD_COLORS = [
    "#AA0DFE",
    "#3283FE",
    "#85660D",
    "#782AB6",
    "#565656",
    "#1C8356",
    "#16FF32",
    "#F7E1A0",
    "#E2E2E2",
    "#1CBE4F",
    "#C4451C",
    "#DEA0FD",
    "#FE00FA",
    "#325A9B",
    "#FEAF16",
    "#F8A19F",
    "#90AD1C",
    "#F6222E",
    "#1CFFCE",
    "#2ED9FF",
    "#B10DA1",
    "#C075A6",
    "#FC1CBF",
    "#B00068",
    "#FBE426",
    "#FA0087",
    "#C8C8C8"
]


class analytic(object):

    def __init__(self, market:_market):
        self.market = market
        self.__caplim = 100000000000
        return

    @property
    def caplim(self) -> int:
        return self.__caplim

    @caplim.setter
    def caplim(self, lim:int):
        self.__caplim = lim
        return

    @property
    def target(self) -> list or np.array or pd.Series:
        if not hasattr(self, '__target'):
            self.__setattr__('__target', self.market.icm[self.market.icm.시가총액 >= self.caplim].index)
        return self.__getattribute__('__target')

    @target.setter
    def target(self, list_or_kind:list or np.array or pd.Series or str):
        if isinstance(list_or_kind, str):
            self.__setattr__('__target', self.market.get_deposit(label=list_or_kind))
            return
        self.__setattr__('__target', list_or_kind)
        return

    def _collect(self):
        for ticker in self.target:
            set

    def __iscoll__(self):
        if not hasattr(self, 'is_coll'):
            for ticker in self.target:
                self.__setattr__(f'A{ticker}', stock(ticker=ticker, endate=self.date, period=5))
            self.__setattr__('is_coll', True)
        return

    def __reset__(self):
        for ticker in self.target:
            if not hasattr(self, f'A{ticker}'):
                self.__setattr__(f'A{ticker}', view_stock(ticker=ticker, endate=self.date, period=5))
        return

    def get_axis_data(self, col:str, axis:str) -> pd.DataFrame:
        data = self.baseline[['종목명', '섹터', '섹터색상', col]].copy()
        data[f'{axis}norm'] = stats.norm.pdf(data[col], data[col].mean(), data[col].std())
        return data

    def append(self, func) -> None:
        self.__iscoll__()
        self.__setattr__('__baseline', pd.concat(objs=[self.baseline, func(obj=self, target=self.target)], axis=1))
        return

    @property
    def baseline(self) -> pd.DataFrame:
        if not hasattr(self, '__baseline'):
            self.__iscoll__()
            wics = self.wics[self.wics.index.isin(self.target)][['종목명', '섹터']].copy()
            icm  = self.icm.drop(columns=['종목명', '거래대금', '상장주식수', 'BPS', 'DPS'])
            perf = self.performance(tickers=self.target)
            df = wics.join(icm, how='left').join(perf, how='left')
            df['시가총액'] = round(np.log(df.시가총액), 2)
            colors = dict(zip(df.섹터.drop_duplicates().tolist(), CD_COLORS))
            df['섹터색상'] = df.섹터.apply(lambda x:colors[x])
            self.__setattr__('__baseline', df)
        return self.__getattribute__('__baseline')
