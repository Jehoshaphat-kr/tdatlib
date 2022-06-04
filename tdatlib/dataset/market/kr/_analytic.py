from tdatlib.dataset.market.kr.api import KR as _market
from tdatlib.viewer.stock import KR as _stock
from scipy import stats
from tqdm import tqdm
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

    @property
    def baseline(self) -> pd.DataFrame:
        if not hasattr(self, '__baseline'):
            _wics = self.market.wics[self.market.wics.index.isin(self.target)].copy()
            _icm  =self.market.icm[self.market.icm.index.isin(self.target)].copy()
            _baseline = pd.concat(
                objs=[_wics, _icm.drop(columns=['종목명', '거래대금', '상장주식수', 'BPS', 'DPS'])],
                axis=1
            )
            self.__setattr__('__baseline', _baseline)
        return self.__getattribute__('__baseline')

    @property
    def frame(self) -> pd.DataFrame:
        if hasattr(self, '__frame'):
            return self.__getattribute__('__frame')
        return self.baseline

    def init(self, period:int=5, endate:str=str()):
        _return = self.market.get_returns(tickers=self.target) if not endate else list()

        proc = tqdm(self.target)
        for ticker in proc:
            proc.set_description(desc=f'Initialize {ticker}...')
            df = _stock(ticker=ticker, period=period, endate=endate)
            if endate:
                _return.append(df.technical.src.ohlcv_returns)
            self.__setattr__(f'__A{ticker}', df)

        if endate:
            _return = pd.concat(objs=_return, axis=0)
        self.__setattr__('__frame', pd.concat(objs=[self.baseline, _return], axis=1))
        return

    def axis(self, columns:list, key:str) -> pd.dataFrame:
        data = self.baseline[['종목명', '섹터'] + columns].copy()
        data[f'{key}_norm'] = stats.norm.pdf(data[key], data[key].mean(), data[key].std())
        return data

    def append(self, df:pd.Series or pd.DataFrame) -> None:
        self.__setattr__('__frame', pd.concat(
            objs=[self.frame, df],
            axis=1
        ))
        return