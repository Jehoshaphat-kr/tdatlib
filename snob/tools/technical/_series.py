import numpy as np
import pandas as pd


def zc(series:pd.Series or np.array):
    """
    Detect Zero-Crossings
    :param series:
    :return:
    """
    return np.where(np.diff(np.sign(series)))[0]


class evaluate(object):
    __td = 20
    __yd = 5.0
    def __init__(self, ohlcv:pd.DataFrame, buysell:pd.DataFrame, name:str):
        self.ohlcv, self.buysell, self.name = ohlcv, buysell, name
        return

    @property
    def forward_td(self) -> int:
        return self.__td

    @forward_td.setter
    def forward_td(self, td:int):
        self.__td = td

    @property
    def target_yd(self) -> float:
        return self.__yd

    @target_yd.setter
    def target_yd(self, yd: int or float):
        self.__yd = yd

    @property
    def edges(self) -> pd.DataFrame:
        """
        Buy Signal 기준 {forward_td} 기간 내 최대/최소 수익률 산출
        :return:
        """
        attr = f'__edges_{self.forward_td}'
        if hasattr(self, attr):
            return self.__getattribute__(attr)

        raw = pd.concat(objs=[self.ohlcv, self.buysell], axis=1)[['시가', '고가', '저가', '종가', 'buy']].copy()
        raw['n'] = np.arange(0, len(raw), 1)
        raw['최대'] = np.nan
        raw['최소'] = np.nan

        ns = raw[~raw['buy'].isna()]['n']
        for n in ns:
            sampled = raw.iloc[n:n+self.forward_td]
            if not sampled.empty:
                sp = sampled[['시가', '고가', '저가', '종가']].values.flatten()
                mm = [round(100 * (p / sp[0] - 1), 2) for p in sp]
                raw.at[raw.index[n], '최대'] = max(mm)
                raw.at[raw.index[n], '최소'] = min(mm)
        self.__setattr__(attr, raw.drop(columns=['n']).dropna())
        return self.__getattribute__(attr)

    def eval(self):
        attr = f'__edges_{self.forward_td}_{self.target_yd}'
        if hasattr(self, attr):
            return self.__getattribute__(attr)

        copy = self.edges.copy()
        maxi = copy.최대.dropna()
        mini = copy.최소.dropna()
        mxdt = maxi[maxi==maxi.max()].index[0]
        mndt = mini[mini==mini.min()].index[0]
        eva = {
            'TRADING DAYS'   : f'{len(self.ohlcv)} DAYS',
            'BUY SIGNALED'   : f'{len(copy)} DAYS',
            'OVER PERFORM'   : f'{len(maxi[maxi >= self.target_yd])} DAYS',
            'SUCCESS RATE'   : f'{round(100 * len(maxi[maxi >= self.target_yd])/len(copy), 2)}%',
            'AVERAGE RISE'   : f'{round(maxi.mean(), 2)}%',
            'AVERAGE DROP'   : f'{round(mini.mean(), 2)}%',
            'BEST CASE'      : f'{round(maxi.max(), 2)}%',
            'BEST CASE DATE' : f'{mxdt.date()}',
            'WORST CASE'     : f'{mini.min()}%',
            'WORST CASE DATE': f'{mndt.date()}'
        }
        return pd.DataFrame(data=eva, index=[self.name])
