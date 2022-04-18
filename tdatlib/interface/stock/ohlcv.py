import pandas as pd
import math, warnings
import yfinance as yf
import numpy as np
from pykrx import stock as krx
from ta import add_all_ta_features
from datetime import datetime, timedelta
from pytz import timezone
from findiff import FinDiff
from scipy.stats import linregress
from scipy.signal import butter, filtfilt
warnings.simplefilter(action='ignore', category=FutureWarning)
np.seterr(divide='ignore', invalid='ignore')


PM_KEY = '종가'


def calc_ta(ohlcv:pd.DataFrame) -> pd.DataFrame:
    return add_all_ta_features(ohlcv.copy(), open='시가', close='종가', low='저가', high='고가', volume='거래량')

def calc_rr(ohlcv:pd.DataFrame) -> pd.DataFrame:
    v = ohlcv[PM_KEY].copy()
    objs = {
        label: 100 * (v[v.index >= v.index[-1] - timedelta(dt)].pct_change().fillna(0) + 1).cumprod() - 100
        for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]
    }
    return pd.concat(objs=objs, axis=1)

def calc_dd(ohlcv:pd.DataFrame) -> pd.DataFrame:
    val, objs = ohlcv[PM_KEY].copy(), dict()
    for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]:
        sampled = val[val.index >= val.index[-1] - timedelta(dt)]
        objs[label] = 100 * (sampled / sampled.cummax()).sub(1)
    return pd.concat(objs=objs, axis=1)

def calc_sma(ohlcv) -> pd.DataFrame:
    return pd.concat(objs={f'SMA{w}D': ohlcv[PM_KEY].rolling(w).mean() for w in [5, 10, 20, 60, 120]}, axis=1)

def calc_ema(ohlcv) -> pd.DataFrame:
    return pd.concat(objs={f'EMA{w}D': ohlcv[PM_KEY].ewm(span=w).mean() for w in [5, 10, 20, 60, 120]}, axis=1)

def calc_iir(ohlcv) -> pd.DataFrame:
    objs, price = dict(), ohlcv[PM_KEY]
    for win in [5, 10, 20, 60, 120]:
        cutoff = (252 / win) / (252 / 2)
        a, b = butter(N=1, Wn=cutoff)
        objs[f'IIR{win}D'] = pd.Series(data=filtfilt(a, b, price), index=price.index)
    return pd.concat(objs=objs, axis=1)

def calc_perf(ohlcv:pd.DataFrame, ticker:str) -> pd.DataFrame:
    val, data = ohlcv[PM_KEY], dict()
    for label, dt in (('R1D', 1), ('R1W', 5), ('R1M', 21), ('R3M', 63), ('R6M', 126), ('R1Y', 252)):
        data[label] = round(100 * val.pct_change(periods=dt)[-1], 2)
    return pd.DataFrame(data=data, index=[ticker])

def calc_cagr(ohlcv:pd.DataFrame, ticker:str) -> pd.DataFrame:
    val, objs = ohlcv[PM_KEY].copy(), dict()
    for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]:
        sampled = val[val.index >= val.index[-1] - timedelta(dt)]
        objs[label] = round(100 * ((sampled[-1] / sampled[0]) ** (1 / (dt / 365)) - 1), 2)
    return pd.DataFrame(data=objs, index=[ticker])

def calc_volatility(ohlcv:pd.DataFrame, ticker:str) -> pd.DataFrame:
    val, objs = ohlcv[PM_KEY].copy(), dict()
    for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]:
        sampled = val[val.index >= val.index[-1] - timedelta(dt)]
        objs[label] = round(100 * (np.log(sampled / sampled.shift(1)).std() * (252 ** 0.5)), 2)
    return pd.DataFrame(data=objs, index=[ticker])

def calc_fiftytwo(ohlcv:pd.DataFrame, ticker:str) -> pd.DataFrame:
    frame = ohlcv[ohlcv.index >= (ohlcv.index[-1] - timedelta(365))][PM_KEY]
    close, _max, _min = frame[-1], frame.max(), frame.min()
    by_max, by_min = round(100 * (close/_max - 1), 2), round(100 * (close/_min - 1), 2)
    return pd.DataFrame(data={'52H': _max, '52L': _min, 'pct52H': by_max, 'pct52L': by_min}, index=[ticker])


class calc_trend(object):

    __avg_slope_high, __avg_slope_low = dict(), dict()

    def __init__(self, ohlcv: pd.DataFrame):
        self.ohlcv = ohlcv
        ohlcv_1y = ohlcv[ohlcv.index >= (ohlcv.index[-1] - timedelta(365))].copy()
        _, mx = self.calc_extrema(h=ohlcv_1y.고가, accuracy=2)
        mn, _ = self.calc_extrema(h=ohlcv_1y.저가, accuracy=2)
        self.pivot = pd.concat(objs={'저점': ohlcv_1y.저가.iloc[mn], '고점': ohlcv_1y.고가.iloc[mx]}, axis=1)
        return

    @staticmethod
    def calc_extrema(h:pd.Series or np.array, accuracy:int=2):
        """
        Customized Pivot Detection
        Originally from PyPI: trendln @https://github.com/GregoryMorse/trendln
        :param h: 시계열 1-D 데이터
        :param accuracy: FinDiff 파라미터
        """
        dx = 1
        d_dx, d2_dx2 = FinDiff(0, dx, 1, acc=accuracy), FinDiff(0, dx, 2, acc=accuracy)
        def get_peak(h):
            arr = np.asarray(h, dtype=np.float64)
            mom, momacc = d_dx(arr), d2_dx2(arr)
            def __diff_extrema(func):
                return [x for x in range(len(mom)) if func(x) and ( mom[x] == 0 or (
                    x != len(mom) - 1 and (
                        mom[x] > 0 > mom[x + 1] and h[x] >= h[x + 1] or mom[x] < 0 < mom[x + 1] and h[x] <= h[x + 1]
                    ) or x != 0 and (
                        mom[x - 1] > 0 > mom[x] and h[x - 1] < h[x] or mom[x - 1] < 0 < mom[x] and h[x - 1] > h[x]
                    )
                ))]

            return lambda x: momacc[x] > 0, lambda x: momacc[x] < 0, __diff_extrema

        minFunc, maxFunc, diff_extrema = get_peak(h)
        return diff_extrema(minFunc), diff_extrema(maxFunc)

    @staticmethod
    def calcEdgeLine(price: pd.DataFrame, key: str) -> pd.Series:
        tip_v = price[key].max() if key == '고가' else price[key].min()
        tip = price[price[key] == tip_v]
        tip_i, tip_n = tip.index[-1], tip['N'].values[-1]
        regression = lambda x, y: ((y - tip_v) / (x - tip_n), y - ((y - tip_v) / (x - tip_n)) * x)

        r_cond, l_cond = price.index > tip_i, price.index < tip_i
        r_side = price[r_cond].drop_duplicates(keep='last').sort_values(by=key, ascending=not key == '고가')
        l_side = price[l_cond].drop_duplicates(keep='first').sort_values(by=key, ascending=not key == '고가')

        r_regress, l_regress = pd.Series(dtype=float), pd.Series(dtype=float)
        for n, side in enumerate((r_side, l_side)):
            n_prev = len(price)
            for x, y in zip(side.N, side[key]):
                slope, intercept = regression(x=x, y=y)
                regress = slope * price.N + intercept
                cond = price[key] >= regress if key == '고가' else price[key] <= regress

                n_curr = len(price[cond])
                if n_curr < n_prev and n_curr < 3:
                    if n:
                        l_regress = regress
                    else:
                        r_regress = regress
                    break
                n_prev = n_curr

        if r_regress.empty:
            return l_regress
        if l_regress.empty:
            return r_regress
        r_error = math.sqrt((r_regress - price[key]).pow(2).sum())
        l_error = math.sqrt((l_regress - price[key]).pow(2).sum())
        return r_regress if r_error < l_error else l_regress

    @property
    def avg(self) -> pd.DataFrame:
        if hasattr(self, '__avg'):
            return self.__getattribute__('__avg')

        objs = dict()
        for gap, days in [('2M', 61), ('3M', 92), ('6M', 183), ('1Y', 365)]:
            since = self.ohlcv.index[-1] - timedelta(days)
            price = self.ohlcv[self.ohlcv.index >= since].reset_index(level=0).copy()
            pivot = self.pivot[self.pivot.index >= since].copy()

            price['N'] = (price.날짜.diff()).dt.days.fillna(1).astype(int).cumsum()
            price.set_index(keys='날짜', inplace=True)

            y_l, y_h = pivot.저점.dropna(), pivot.고점.dropna()
            x_l, x_h = price[price.index.isin(y_l.index)]['N'], price[price.index.isin(y_h.index)]['N']

            s_l, i_l, _, _, _ = linregress(x=x_l, y=y_l)
            s_h, i_h, _, _, _ = linregress(x=x_h, y=y_h)

            lo, hi = s_l * price['N'] + i_l, s_h * price['N'] + i_h
            self.__avg_slope_low[gap], self.__avg_slope_high[gap] = s_l, s_h

            objs[gap] = pd.concat(objs={'resist': hi, 'support': lo}, axis=1)
        self.__setattr__('__avg', pd.concat(objs=objs, axis=1))
        return self.__getattribute__('__avg')

    @property
    def avg_slope_high(self) -> dict:
        if not self.__avg_slope_high:
            _ = self.avg
        return self.__avg_slope_high

    @property
    def avg_slope_low(self) -> dict:
        if not self.__avg_slope_low:
            _ = self.avg
        return self.__avg_slope_low

    @property
    def bound(self) -> pd.DataFrame:
        objs = dict()
        for gap, days in [('2M', 61), ('3M', 92), ('6M', 183), ('1Y', 365)]:
            since = self.ohlcv.index[-1] - timedelta(days)
            price = self.ohlcv[self.ohlcv.index >= since].reset_index(level=0).copy()
            price['N'] = (price.날짜.diff()).dt.days.fillna(1).astype(int).cumsum()
            price.set_index(keys='날짜', inplace=True)

            objs[gap] = pd.concat(
                objs={
                    'resist': self.calcEdgeLine(price=price, key='고가'),
                    'support': self.calcEdgeLine(price=price, key='저가')
                }, axis=1
            )
        return pd.concat(objs=objs, axis=1)