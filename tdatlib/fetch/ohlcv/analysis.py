import math
import yfinance as yf
import pandas as pd
import numpy as np
from pykrx import stock as krx
from datetime import datetime, timedelta
from pytz import timezone
from findiff import FinDiff
from scipy.stats import linregress


def getName(ticker:str, namebook:pd.DataFrame=pd.DataFrame()) -> str:
    """
    종목명 찾기
    """
    if ticker.isalpha():
        return ticker
    elif len(ticker) == 4:
        return krx.get_index_ticker_name(ticker=ticker)
    elif len(ticker) == 6:
        if not namebook.empty and ticker in namebook.index:
            return namebook.loc[ticker, '종목명']
        name = krx.get_market_ticker_name(ticker=ticker)
        if isinstance(name, pd.DataFrame):
            return krx.get_etf_ticker_name(ticker=ticker)
        return name

def getOhlcv(ticker:str, period:int=5) -> pd.DataFrame:
    """
    주가 시계열 데이터
    :param ticker: 중목코드/티커
    :param period: 연단위 기간
                      시가        고가        저가        종가     거래량
    Date
    2017-03-14   49.222000   51.624001   49.203999   51.599998  37992000
    2017-03-15   51.400002   52.200001   50.854000   51.146000  26654000
    2017-03-16   52.480000   53.150002   51.812000   52.410000  35661000
    ...                ...         ...         ...         ...       ...
    2022-03-10  851.450012  854.450012  810.359985  838.299988  19549500
    2022-03-11  840.200012  843.799988  793.770020  795.349976  22272800
    2022-03-14  780.609985  800.699890  756.344971  795.039978   7864541
    """
    curr = datetime.now(timezone('Asia/Seoul' if ticker.isdigit() else 'US/Eastern'))
    prev = curr - timedelta(365 * period)
    if ticker.isdigit():
        func = krx.get_index_ohlcv_by_date if len(ticker) == 4 else krx.get_market_ohlcv_by_date
        return func(fromdate=prev.strftime("%Y%m%d"), todate=curr.strftime("%Y%m%d"), ticker=ticker)
    else:
        o_names = ['Open', 'High', 'Low', 'Close', 'Volume']
        c_names = ['시가', '고가', '저가', '종가', '거래량']
        ohlcv = yf.Ticker(ticker).history(period=f'{period}y')[o_names]
        ohlcv.index.name = '날짜'
        return ohlcv.rename(columns=dict(zip(o_names, c_names)))

def getRelReturns(ohlcv:pd.DataFrame, key:str='종가') -> pd.DataFrame:
    """
    상대 수익률
    :param ohlcv: 가격
    :param key: 시/고/저/종가
                       3M         6M         1Y          2Y           3Y
    Date
    2019-03-15        NaN        NaN        NaN         NaN     0.000000
    2019-03-18        NaN        NaN        NaN         NaN    -2.156627
    2019-03-19        NaN        NaN        NaN         NaN    -2.890025
    ...               ...        ...        ...         ...          ...
    2022-03-10 -13.256277  12.826378  18.413988  841.761957  1421.802291
    2022-03-11 -17.700562   7.045757  12.347088  793.511106  1343.833273
    2022-03-14 -18.233458   6.352626  11.619630  787.725541  1334.484321
    """
    v = ohlcv[key].copy()
    objs = {
        label: 100 * (v[v.index >= v.index[-1] - timedelta(dt)].pct_change().fillna(0) + 1).cumprod() - 100
        for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095)]
    }
    return pd.concat(objs=objs, axis=1)

def getPerf(ohlcv:pd.DataFrame, key:str='종가', name:str=str()) -> pd.DataFrame:
    """
    기간별 수익률
    :param ohlcv: 가격
    :param key: 시/고/저/종가
    :param name: 종목명
                 R1D   R1W   R1M   R3M   R6M    R1Y
    SK하이닉스 -0.85 -6.83 -7.94 -4.53  8.92 -17.14
    """
    data = [round(100 * ohlcv[key].pct_change(periods=dt)[-1], 2) for dt in [1, 5, 21, 63, 126, 252]]
    return pd.DataFrame(data=data, columns=[name], index=['R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y']).T

def getFiftyTwo(ohlcv:pd.DataFrame, key:str='종가', name:str=str()) -> pd.DataFrame:
    """
    52주 최고/최저 가격 및 대비 수익률
    :param ohlcv: 가격
    :param key: 시/고/저/종가
    :param name: 종목명
                     52H      52L  pct52H  pct52L
    SK하이닉스  144000.0  91500.0  -19.44   26.78
    """
    frame = ohlcv[ohlcv.index >= (ohlcv.index[-1] - timedelta(365))][key]
    close, _max, _min = frame[-1], frame.max(), frame.min()
    by_max, by_min = round(100 * (close/_max - 1), 2), round(100 * (close/_min - 1), 2)
    return pd.DataFrame(
        data=[_max, _min, by_max, by_min],
        columns=[name],
        index=['52H', '52L', 'pct52H', 'pct52L']
    ).T

def getExtrema(h:pd.Series or np.array, accuracy:int=2):
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
            return [
                x for x in range(len(mom)) if func(x) and (
                    mom[x] == 0 or
                    (
                        x != len(mom) - 1 and (
                            mom[x] > 0 > mom[x + 1] and h[x] >= h[x + 1] or mom[x] < 0 < mom[x + 1] and h[x] <= h[x + 1]
                        ) or x != 0 and (
                            mom[x - 1] > 0 > mom[x] and h[x - 1] < h[x] or mom[x - 1] < 0 < mom[x] and h[x - 1] > h[x]
                        )
                    )
                )
            ]
        return lambda x: momacc[x] > 0, lambda x: momacc[x] < 0, __diff_extrema

    minFunc, maxFunc, diff_extrema = get_peak(h)
    return diff_extrema(minFunc), diff_extrema(maxFunc)


class trend:
    __avg_slope_high, __avg_slope_low = None, None
    def __init__(self, ohlcv: pd.DataFrame, pivot: pd.DataFrame, gap: str = str()):
        days = {'2M': 61, '3M': 92, '6M': 183, '1Y': 365}[gap]
        since = ohlcv.index[-1] - timedelta(days)

        self.price = ohlcv[ohlcv.index >= since].reset_index(level=0).copy()
        self.price['N'] = (self.price.날짜.diff()).dt.days.fillna(1).astype(int).cumsum()
        self.price.set_index(keys='날짜', inplace=True)
        self.pivot = pivot[pivot.index >= since]
        return

    @property
    def avg(self) -> pd.DataFrame:
        """
        평균 선형 회귀
        """
        y_l, y_h = self.pivot.저점.dropna(), self.pivot.고점.dropna()
        x_l, x_h = self.price[self.price.index.isin(y_l.index)]['N'], self.price[self.price.index.isin(y_h.index)]['N']

        self.__avg_slope_low, i_l, _, _, _ = linregress(x=x_l, y=y_l)
        lo = self.__avg_slope_low * self.price['N'] + i_l

        self.__avg_slope_high, i_h, _, _, _ = linregress(x=x_h, y=y_h)
        hi = self.__avg_slope_high * self.price['N'] + i_h
        return pd.concat(objs={'support': lo, 'resist': hi}, axis=1)

    @property
    def avg_slope_high(self) -> float:
        if not self.__avg_slope_high:
            _ = self.avg
        return self.__avg_slope_high

    @property
    def avg_slope_low(self) -> float:
        if not self.__avg_slope_low:
            _ = self.avg
        return self.__avg_slope_low

    @property
    def bound(self) -> pd.DataFrame:
        objs = {'resist': self.calcEdgeLine(key='고가'), 'support': self.calcEdgeLine(key='저가')}
        return pd.concat(objs=objs, axis=1)

    def calcEdgeLine(self, key:str) -> pd.Series:
        tip_v = self.price[key].max() if key == '고가' else self.price[key].min()
        tip = self.price[self.price[key] == tip_v]
        tip_i, tip_n = tip.index[-1], tip['N'].values[-1]
        regression = lambda x, y: ((y - tip_v) / (x - tip_n), y - ((y - tip_v) / (x - tip_n)) * x)

        r_cond, l_cond = self.price.index > tip_i, self.price.index < tip_i
        r_side = self.price[r_cond].drop_duplicates(keep='last').sort_values(by=key, ascending=not key == '고가')
        l_side = self.price[l_cond].drop_duplicates(keep='first').sort_values(by=key, ascending=not key == '고가')

        r_regress, l_regress = pd.Series(dtype=float), pd.Series(dtype=float)
        for n, side in enumerate((r_side, l_side)):
            n_prev = len(self.price)
            for x, y in zip(side.N, side[key]):
                slope, intercept = regression(x=x, y=y)
                regress = slope * self.price.N + intercept
                cond = self.price[key] >= regress if key == '고가' else self.price[key] <= regress

                n_curr = len(self.price[cond])
                if n_curr < n_prev and n_curr < 3:
                    if n: l_regress = regress
                    else: r_regress = regress
                    break
                n_prev = n_curr

        if r_regress.empty:
            return l_regress
        if l_regress.empty:
            return r_regress
        r_error = math.sqrt((r_regress - self.price[key]).pow(2).sum())
        l_error = math.sqrt((l_regress - self.price[key]).pow(2).sum())
        return r_regress if r_error < l_error else l_regress


if __name__ == "__main__":
    ticker = '035720'
    # ticker = '1028'
    # ticker = 'TSLA'

    ohlcv = getOhlcv(ticker=ticker)
    print(ohlcv)

    # rel_returns = getRelReturns(ohlcv=ohlcv, key='종가')
    # print(rel_returns)

    performance = getPerf(ohlcv=ohlcv)
    print(performance)

    # fifty_two = getFiftyTwo(ohlcv=ohlcv)
    # print(fifty_two)