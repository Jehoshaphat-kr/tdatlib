from typing import Union
from scipy.stats import linregress
import pandas as pd
import numpy as np
import math, os


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DIR_ETF = f'{ROOT}/archive/category/etf.csv'


def normalize(series:pd.Series, lim:Union[list, tuple]=None) -> pd.Series:
    """
    :param series : 시계열(index 날짜/시간) 1D 데이터
    :param lim    : 정규화 범위
    :return:
    """
    lim = lim if lim else [0, 1]
    minima, maxima = tuple(lim)
    return (maxima - minima) * (series - series.min()) / (series.max() - series.min()) + minima


def fit(series:pd.Series, rel:bool=False) -> (pd.Series, float):
    """
    :param series : 시계열(index 날짜/시간) 1D 데이터
    :param rel    : 상대 배율 사용 여부
    :return: (회귀 데이터, 기울기)
    """
    data = pd.DataFrame(data={'Time':series.index, 'Data':series})

    x = (data.Time.diff()).dt.days.fillna(1).astype(int).cumsum()
    y = 100 * ((data.Data.pct_change().fillna(0) + 1).cumprod() - 1) if rel else data.Data
    s, i, _, _, _ = linregress(x=x, y=y)
    regression = s * x + i
    regression.name = 'Regression'
    _ = pd.concat(objs=[data, regression], axis=1)
    return _[['Time', 'Regression']].set_index(keys='Time'), s * (100 if rel else 1)


def delimit(price:pd.DataFrame, key:str) -> pd.Series:
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


def intersect(series:pd.Series, point:float=0.0) -> pd.DataFrame:
    f_fall = f_zc = lambda x: 1 if x < 0 else np.nan
    f_rise = lambda x: 1 if x > 0 else np.nan

    base = series - point
    prod = base * base.shift(1)
    cross = np.vectorize(f_zc)(prod) * series
    rise = np.vectorize(f_rise)(cross) * cross
    fall = np.vectorize(f_fall)(cross) * cross
    return pd.concat(objs={series.name:series, 'crossing':cross, 'rise':rise, 'fall':fall}, axis=1)