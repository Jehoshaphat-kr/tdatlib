import numpy as np
import pandas as pd


def zc(series:pd.Series or np.array):
    """
    Detect Zero-Crossings
    :param series:
    :return:
    """
    return np.where(np.diff(np.sign(series)))[0]


def ev(data:pd.DataFrame, td:int=20):
    """
    Evaulate [Buy] Signal condition
    :param data : ohlcv + "Buy" Signal Table
    :param td   : target trading days
    :return:
    """
    raw = data.copy()
    raw['n'] = np.arange(0, len(raw), 1)
    ns = raw[~raw.buy.isna()]['n']

    for n in ns:
        sampled = data[n:td]
        if sampled.empty:
            continue
        sp = sampled[['시가', '고가', '저가', '종가']].values.flatten()
        mm = [round(100 * (p / sp[0] - 1), 2) for p in sp]
        raw.at[ns.index[n], '최대'] = max(mm)
        raw.at[ns.index[n], '최소'] = min(mm)
    return raw.drop(columns=['n'])