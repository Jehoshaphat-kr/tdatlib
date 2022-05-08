from tdatlib.viewer.stock import view_stock
from tdatlib.dataset.fetch.market import fetch_market
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


class interface_market(fetch_market):

    def __init__(self, date:str=str()):
        super().__init__()
        self.date = date
        return

    def __iscoll__(self):
        if not hasattr(self, 'is_coll'):
            for ticker in self.target:
                self.__setattr__(f'A{ticker}', view_stock(ticker=ticker, endate=self.date, period=5))
            self.__setattr__('is_coll', True)
        return

    def __reset__(self):
        for ticker in self.target:
            if not hasattr(self, f'A{ticker}'):
                self.__setattr__(f'A{ticker}', view_stock(ticker=ticker, endate=self.date, period=5))
        return

    def set_target(self, category_or_tickers:str or list):
        for attr in ['__baseline']:
            if hasattr(self, attr):
                self.__delattr__(attr)

        if isinstance(category_or_tickers, list):
            self.__setattr__('__target', category_or_tickers)
            return

        if isinstance(category_or_tickers, str):
            if category_or_tickers.lower() == 'kospi':
                self.__setattr__('__target', self.kospi)
            elif category_or_tickers.lower() == 'kosdaq':
                self.__setattr__('__target', self.kosdaq)
            elif category_or_tickers.lower() == 'kospi200':
                self.__setattr__('__target', self.kospi200)
            elif category_or_tickers.lower() == 'kosdaq150':
                self.__setattr__('__target', self.kosdaq150)
            elif category_or_tickers.lower() == 'midcap':
                self.__setattr__('__target', self.kospi_midcap + self.kosdaq_midcap)
            elif category_or_tickers.lower() == 'all':
                self.__setattr__('__target', self.kospi + self.kosdaq)
            return

        raise KeyError(f'Parameter category = {category_or_tickers} is not the right target')

    def reset_target(self):
        self.__setattr__('__target', self.kospi200 + self.kosdaq150)
        if hasattr(self, '__baseline'):
            self.__delattr__('__baseline')
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
    def target(self) -> list:
        if not hasattr(self, '__target'):
            self.reset_target()
        return self.__getattribute__('__target')

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


if __name__ == "__main__":
    t_tickers = ['005930', '000660', '000990', '058470', '005290', '357780']

    tester = interface_market()

    # tester.set_target(category_or_tickers=t_tickers)
    print(tester.baseline)
    # print(tester.get_axis_data(col='R1Y', axis='x'))

    # tester.append(func=new_attrib)
    # print(tester.baseline)