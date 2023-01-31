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
    __sd = 1000000
    def __init__(self, ohlcv:pd.DataFrame, buysell:pd.DataFrame, name:str):
        self.ohlcv, self.buysell, self.name = ohlcv, buysell, name
        return

    @property
    def seed(self) -> int or float:
        return self.__sd

    @seed.setter
    def seed(self, seed:int or float):
        self.__sd = seed

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

    def analyze(
        self,
        seed:int or float=-1,
        depo:int or float=0,
        risk_free:int or float=2.0
    ):
        seed = self.seed if seed == -1 else seed
        depo = self.seed if depo == 0 else depo
        cash, account, paper, state = seed, 0, 0, 'h'

        base = pd.concat(objs=[self.ohlcv, self.buysell], axis=1)
        bs = base[~base.buy.isna() | ~base.sell.isna()].copy()
        indices = base.index.tolist()
        for r in bs[['buy', 'sell']].itertuples():
            i, b, s = tuple(r)
            if not b is np.nan:
                p_buy = base.loc[indices[indices.index(i) + 1], '시가']
                print("B@:", i, b, p_buy)
            # if r[-1]:
            #     print('B: ', r)
            # if r[-2]:
            #     print('S: ', r)
        return

    @property
    def edges(self) -> pd.DataFrame:
        """
        :return:
        """
        attr = f'__edges_{self.forward_td}'
        if hasattr(self, attr):
            return self.__getattribute__(attr)

        raw = pd.concat(objs=[self.ohlcv, self.buysell], axis=1)[['시가', '고가', '저가', '종가', 'buy']].copy()
        raw['n'] = np.arange(0, len(raw), 1)
        raw['최대'] = np.nan
        raw['최소'] = np.nan
        raw['손절'] = np.nan

        ns = raw[~raw['buy'].isna()]['n']
        for n in ns:
            sampled = raw.iloc[(n + 1) : (n + 1) + self.forward_td]
            if not sampled.empty:
                sp = sampled[['시가', '고가', '저가', '종가']].values.flatten()
                mm = [round(100 * (p / sp[0] - 1), 2) for p in sp]
                raw.at[raw.index[n], '최대'] = max(mm)
                raw.at[raw.index[n], '최소'] = min(mm)
                if max(mm) < self.target_yd:
                    raw.at[raw.index[n], '손절'] = round(100 * (sp[-1] / sp[0] - 1), 2)
        _t = raw.drop(columns=['n'])
        self.__setattr__(attr, _t[~_t.buy.isna()])
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
            'TRADING DAYS'   : len(self.ohlcv),
            'BUY SIGNALED'   : len(copy),
            'OVER PERFORM'   : len(maxi[maxi >= self.target_yd]),
            'SUCCESS RATE'   : round(100 * len(maxi[maxi >= self.target_yd])/len(copy), 2),
            'CUT LOSS RATE'  : round(copy['손절'].dropna().mean(), 2),
            'AVERAGE RISE'   : round(maxi.mean(), 2),
            'AVERAGE DROP'   : round(mini.mean(), 2),
            'BEST CASE'      : round(maxi.max(), 2),
            'BEST CASE DATE' : mxdt.date(),
            'WORST CASE'     : mini.min(),
            'WORST CASE DATE': mndt.date()
        }
        return pd.DataFrame(data=eva, index=[self.name])


if __name__ == "__main__":

    from snob.stock import kr
    from snob.tools import bollinger_band

    rw = kr('012330')
    bb = bollinger_band(ohlcv=rw.ohlcv, name=rw.name, unit=rw.curr)
    es = evaluate(ohlcv=rw.ohlcv, buysell=bb.obos_signal, name=rw.name)
    es.analyze()