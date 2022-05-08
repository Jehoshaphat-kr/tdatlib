from typing import Union
from scipy.stats import linregress
import pandas as pd


def normalize(series:pd.Series, lim:Union[list, tuple]=None) -> pd.Series:
    """
    :param series : 시계열(index 날짜/시간) 1D 데이터
    :param lim    : 정규화 범위
    :return:
    """
    lim = lim if lim else [0, 1]
    minima, maxima = tuple(lim)
    return (maxima - minima) * (series - series.min()) / (series.max() - series.min()) + minima


def fit_timeseries(series:pd.Series, rel:bool=False) -> (pd.Series, float):
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


if __name__ == "__main__":
    import tdatlib

    viewer = tdatlib.view_stock(ticker='035420', period=1)

    # norm = normalize(viewer.)