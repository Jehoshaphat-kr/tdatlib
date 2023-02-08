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
    __sd = 10000000
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

    def analyze_bs(
        self,
        principle:int or float=-1,
        div_buy:int or float=-1,
        risk_free:int or float=1.5
    ):
        """

        :param principle:
        :param div_buy:
        :param risk_free:
        :return:
        """
        cash = self.seed if principle == -1 else principle # Cash Seed Money
        stock = 0

        base = pd.concat(objs=[self.ohlcv, self.buysell], axis=1)
        indices = base.index.tolist()
        history = [
            ['EVENT', 'DATE', 'STOCK', 'CASH', 'TOTAL'],
            ['START', indices[0].date(), 0, cash, cash]
        ]
        for i, b, s in base[~base.buy.isna() | ~base.sell.isna()][['buy', 'sell']].itertuples():
            next_tday = indices[indices.index(i) + 1]
            o = base.loc[next_tday, '시가']
            capa = cash if div_buy == -1 else div_buy
            if str(s) == 'nan' and capa <= cash: # Case Buy
                _stock = int(capa / o)
                cash = cash - (o * _stock)
                stock += _stock
                history.append(['BUY', i.date(), stock, cash, stock * base.loc[next_tday, '종가'] + cash])
            elif str(b) == 'nan' and stock > 0: # Case Sell
                cash += (stock * o)
                stock = 0
                history.append(['SELL', i.date(), 0, cash, cash])

        d = (indices[-1] - indices[0]).days
        principle = self.seed if principle == -1 else principle
        estimated = base.loc[indices[-1], '종가'] * stock + cash
        estimated_no_risk = principle * (1.0 + (1-0.154) * risk_free / 100) ** int(d/365)
        history.append(['END', indices[-1].date(), stock, cash, estimated])
        history = pd.DataFrame(columns=history.pop(0), data=history)
        data = dict(
            START=indices[0].date(),
            END=indices[-1].date(),
            PRICE_START=base.loc[indices[0], '종가'],
            PRICE_END=base.loc[indices[-1], '종가'],
            DURATION_DAYS=d,
            DURATION=f'{int(d/365)}Y {int((d - int(d/365) * 365)/30)}M',
            COUNT_BUY=len(history[history.EVENT == 'BUY']),
            COUNT_SELL=len(history[history.EVENT == 'SELL']),
            STATUS="hold" if stock else "sell",
            PRINCIPLE=principle,
            STOCK=stock,
            CASH=cash,
            ESTIMATED=estimated,
            ESTIMATED_NORISK=int(estimated_no_risk),
            YIELD=round(100 * ((estimated / principle) - 1), 2),
            YIELD_NORISK=round(100 * ((estimated_no_risk / principle) - 1), 2),
        )
        data['PREMIUM'] = data['YIELD'] - data['YIELD_NORISK']

        self.__setattr__('__history', history)
        return pd.DataFrame(data=data, index=[self.name])

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
    from datetime import datetime

    rw = kr('005930')
    rw.period = 3
    # rw.limit = [datetime(2010, 12, 1), datetime(2015, 5, 5)]

    bb = bollinger_band(ohlcv=rw.ohlcv, name=rw.name, unit=rw.curr)
    es = evaluate(ohlcv=rw.ohlcv, buysell=bb.obos_signal, name=rw.name)
    estimation = es.analyze(div_buy=1000000)
    # estimation = es.analyze()
    print(estimation.T)

    # bb.figure_full.show()