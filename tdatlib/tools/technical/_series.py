import numpy as np
import pandas as pd


def zc(series:pd.Series or np.array):
    """
    Detect Zero-Crossings
    :param series:
    :return:
    """
    return np.where(np.diff(np.sign(series)))[0]


def ev(data:pd.DataFrame, td:int=20, goal:float=4.0):
    """
    Evaulate [Buy] Signal condition
    :param data : ohlcv + "Buy" Signal Table
    :param td   : target trading days
    :param goal : target performance [%]
    :return:
    """
    raw = data.copy()
    raw['n'] = np.arange(0, len(raw), 1)
    buy = raw.buy.dropna().n

    return