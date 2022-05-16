from tdatlib.dataset.tools.tool import (
    fit,
    delimit
)
from datetime import datetime, timedelta
from pytz import timezone
from pykrx import stock
from ta import add_all_ta_features
from scipy.signal import butter, filtfilt
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
np.seterr(divide='ignore', invalid='ignore')


def fetch_ohlcv(ticker:str, period:int=5) -> pd.DataFrame:
    curr = datetime.now(timezone('Asia/Seoul' if ticker.isdigit() else 'US/Eastern'))
    prev = curr - timedelta(365 * period)
    if ticker.isdigit():
        func = stock.get_index_ohlcv_by_date if len(ticker) == 4 else stock.get_market_ohlcv_by_date
        ohlcv = func(fromdate=prev.strftime("%Y%m%d"), todate=curr.strftime("%Y%m%d"), ticker=ticker)
        trade_stop = ohlcv[ohlcv.시가 == 0].copy()
        if not trade_stop.empty:
            ohlcv.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop['종가']
    else:
        o_names = ['Open', 'High', 'Low', 'Close', 'Volume']
        c_names = ['시가', '고가', '저가', '종가', '거래량']
        ohlcv = yf.Ticker(ticker).history(period=f'{period}y')[o_names]
        ohlcv.index.name = '날짜'
        ohlcv = ohlcv.rename(columns=dict(zip(o_names, c_names)))
    return ohlcv


def calc_btr(ohlcv_ans:pd.DataFrame) -> pd.DataFrame:
    columns = ['시가', '고가', '저가', '종가', '거래량', '등락', '누적', '최대', '최소']
    if ohlcv_ans.empty:
        return pd.DataFrame(columns=columns)
    if len(ohlcv_ans) > 20:
        ohlcv_ans = ohlcv_ans[:20].copy()

    ohlcv_ans['등락'] = round(100 * ohlcv_ans.종가.pct_change().fillna(0), 2)
    ohlcv_ans['누적'] = round(100 * ((ohlcv_ans.종가.pct_change().fillna(0) + 1).cumprod() - 1), 2)
    span = ohlcv_ans[['시가', '고가', '저가', '종가']].values.flatten()
    returns = [round(100 * (p / span[0] - 1), 2) for p in span]
    ohlcv_ans['최대'] = max(returns)
    ohlcv_ans['최소'] = min(returns)
    return ohlcv_ans[columns]


def calc_btl(ohlcv:pd.DataFrame) -> pd.DataFrame:
    data = list()
    for n, i in enumerate(ohlcv[:-20].index):
        sample = ohlcv[n + 1 : n + 21][['시가', '고가', '저가', '종가']]
        span = sample.values.flatten()
        returns = [round(100 * (p / span[0] - 1), 2) for p in span]
        data.append({'날짜':i, '최대': max(returns), '최소': min(returns)})
    btr = pd.DataFrame(data=data).set_index(keys='날짜')
    return pd.concat(objs=[ohlcv, btr], axis=1)


def calc_returns(ohlcv:pd.DataFrame, ticker:str) -> pd.DataFrame:
    val, data = ohlcv.종가, dict()
    for label, dt in (('R1D', 1), ('R1W', 5), ('R1M', 21), ('R3M', 63), ('R6M', 126), ('R1Y', 252)):
        data[label] = round(100 * val.pct_change(periods=dt)[-1], 2)
    return pd.DataFrame(data=data, index=[ticker])


def calc_ta(ohlcv:pd.DataFrame) -> pd.DataFrame:
    return add_all_ta_features(ohlcv.copy(), open='시가', close='종가', low='저가', high='고가', volume='거래량')


def calc_rr(ohlcv:pd.DataFrame) -> pd.DataFrame:
    objs = dict()
    v = ohlcv.종가.copy()
    for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]:
        objs[label] = 100 * (v[v.index >= v.index[-1] - timedelta(dt)].pct_change().fillna(0) + 1).cumprod() - 100
    return pd.concat(objs=objs, axis=1)


def calc_dd(ohlcv:pd.DataFrame) -> pd.DataFrame:
    val, objs = ohlcv.종가.copy(), dict()
    for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]:
        sampled = val[val.index >= val.index[-1] - timedelta(dt)]
        objs[label] = 100 * (sampled / sampled.cummax()).sub(1)
    return pd.concat(objs=objs, axis=1)


def calc_sma(ohlcv:pd.DataFrame) -> pd.DataFrame:
    return pd.concat(objs={f'MA{w}D': ohlcv.종가.rolling(w).mean() for w in [5, 10, 20, 60, 120, 200]}, axis=1)


def calc_ema(ohlcv:pd.DataFrame) -> pd.DataFrame:
    return pd.concat(objs={f'EMA{w}D': ohlcv.종가.ewm(span=w).mean() for w in [5, 10, 20, 60, 120]}, axis=1)


def calc_iir(ohlcv:pd.DataFrame) -> pd.DataFrame:
    objs, price = dict(), ohlcv.종가
    for win in [5, 10, 20, 60, 120]:
        cutoff = (252 / win) / (252 / 2)
        a, b = butter(N=1, Wn=cutoff)
        objs[f'NC{win}D'] = pd.Series(data=filtfilt(a, b, price), index=price.index)
    return pd.concat(objs=objs, axis=1)


def calc_cagr(ohlcv:pd.DataFrame, ticker:str) -> pd.DataFrame:
    val, objs = ohlcv.종가.copy(), dict()
    for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]:
        sampled = val[val.index >= val.index[-1] - timedelta(dt)]
        objs[label] = round(100 * ((sampled[-1] / sampled[0]) ** (1 / (dt / 365)) - 1), 2)
    return pd.DataFrame(data=objs, index=[ticker])


def calc_volatility(ohlcv:pd.DataFrame, ticker:str) -> pd.DataFrame:
    val, objs = ohlcv.종가.copy(), dict()
    for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]:
        sampled = val[val.index >= val.index[-1] - timedelta(dt)]
        objs[label] = round(100 * (np.log(sampled / sampled.shift(1)).std() * (252 ** 0.5)), 2)
    return pd.DataFrame(data=objs, index=[ticker])


def calc_fiftytwo(ohlcv:pd.DataFrame, ticker:str) -> pd.DataFrame:
    frame = ohlcv[ohlcv.index >= (ohlcv.index[-1] - timedelta(365))].종가
    close, _max, _min = frame[-1], frame.max(), frame.min()
    by_max, by_min = round(100 * (close/_max - 1), 2), round(100 * (close/_min - 1), 2)
    return pd.DataFrame(data={'52H': _max, '52L': _min, 'pct52H': by_max, 'pct52L': by_min}, index=[ticker])


def calc_trend(ohlcv:pd.DataFrame) -> pd.DataFrame:
    objs = list()
    for gap, days in [('1M', 30), ('2M', 61), ('3M', 92), ('6M', 183), ('1Y', 365)]:
        since = ohlcv.index[-1] - timedelta(days)
        basis = ohlcv[ohlcv.index >= since]
        fitted, _ = fit(series=0.25 * (basis.시가 + basis.고가 + basis.저가 + basis.종가))
        objs.append(fitted.rename(columns={'Regression':gap}))
    return pd.concat(objs=objs, axis=1)


def calc_bound(ohlcv:pd.DataFrame) -> pd.DataFrame:
    objs = dict()
    for gap, days in [('2M', 61), ('3M', 92), ('6M', 183), ('1Y', 365)]:
        since = ohlcv.index[-1] - timedelta(days)
        price = ohlcv[ohlcv.index >= since].reset_index(level=0).copy()
        price['N'] = (price.날짜.diff()).dt.days.fillna(1).astype(int).cumsum()
        price.set_index(keys='날짜', inplace=True)

        objs[gap] = pd.concat(
            objs={'resist': delimit(price=price, key='고가'), 'support': delimit(price=price, key='저가')},
            axis=1
        )
    return pd.concat(objs=objs, axis=1)