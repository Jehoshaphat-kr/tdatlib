import math
import yfinance as yf
import pandas as pd
import numpy as np
from pykrx import stock as krx
from ta import add_all_ta_features as taf
from datetime import datetime, timedelta
from pytz import timezone
from findiff import FinDiff
from scipy.stats import linregress
from scipy.signal import butter, filtfilt
np.seterr(divide='ignore', invalid='ignore')


class _ohlcv:

    def __init__(self, ticker:str, period:int=5, namebook:pd.DataFrame=pd.DataFrame()):
        self.ticker, self.period, self.namebook = ticker, period, namebook
        self.__setattr__('key', '종가')
        return

    def _get_name(self) -> str:
        """
        종목명 찾기
        """
        if self.ticker.isalpha():
            return self.ticker
        elif len(self.ticker) == 4:
            return krx.get_index_ticker_name(ticker=self.ticker)
        elif len(self.ticker) == 6:
            if not self.namebook.empty and self.ticker in self.namebook.index:
                return self.namebook.loc[self.ticker, '종목명']
            name = krx.get_market_ticker_name(ticker=self.ticker)
            if isinstance(name, pd.DataFrame):
                return krx.get_etf_ticker_name(ticker=self.ticker)
            return name

    def _get_ohlcv(self) -> pd.DataFrame:
        """ 주가 시계열 데이터 """
        curr = datetime.now(timezone('Asia/Seoul' if self.ticker.isdigit() else 'US/Eastern'))
        prev = curr - timedelta(365 * self.period)
        if self.ticker.isdigit():
            func = krx.get_index_ohlcv_by_date if len(self.ticker) == 4 else krx.get_market_ohlcv_by_date
            ohlcv = func(fromdate=prev.strftime("%Y%m%d"), todate=curr.strftime("%Y%m%d"), ticker=self.ticker)
            trade_stop = ohlcv[ohlcv.시가 == 0].copy()
            ohlcv.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop['종가']
        else:
            o_names = ['Open', 'High', 'Low', 'Close', 'Volume']
            c_names = ['시가', '고가', '저가', '종가', '거래량']
            ohlcv = yf.Ticker(self.ticker).history(period=f'{self.period}y')[o_names]
            ohlcv.index.name = '날짜'
            ohlcv = ohlcv.rename(columns=dict(zip(o_names, c_names)))
        self.__setattr__('_ohlcv', ohlcv)
        return ohlcv

    def _get_ta(self) -> pd.DataFrame:
        """ Technical Analysis """
        if not hasattr(self, '_ohlcv'):
            self._get_ohlcv()
        ohlcv = self.__getattribute__('_ohlcv')
        return taf(ohlcv.copy(), open='시가', close='종가', low='저가', high='고가', volume='거래량')

    def _get_relative_return(self) -> pd.DataFrame:
        """ 상대 수익률 """
        if not hasattr(self, '_ohlcv'):
            self._get_ohlcv()
        ohlcv, key = self.__getattribute__('_ohlcv'), self.__getattribute__('key')

        v = ohlcv[key].copy()
        objs = {
            label: 100 * (v[v.index >= v.index[-1] - timedelta(dt)].pct_change().fillna(0) + 1).cumprod() - 100
            for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]
        }
        return pd.concat(objs=objs, axis=1)

    def _get_perf(self) -> pd.DataFrame:
        """ 기간별 수익률 """
        if not hasattr(self, '_ohlcv'):
            self._get_ohlcv()
        ohlcv, key = self.__getattribute__('_ohlcv'), self.__getattribute__('key')

        data = [round(100 * ohlcv[key].pct_change(periods=dt)[-1], 2) for dt in [1, 5, 21, 63, 126, 252]]
        return pd.DataFrame(data=data, columns=[self.ticker], index=['R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y']).T

    def _get_fiftytwo(self) -> pd.DataFrame:
        """ 52주 최고/최저 가격 및 대비 수익률 """
        if not hasattr(self, '_ohlcv'):
            self._get_ohlcv()
        ohlcv, key = self.__getattribute__('_ohlcv'), self.__getattribute__('key')

        frame = ohlcv[ohlcv.index >= (ohlcv.index[-1] - timedelta(365))][key]
        close, _max, _min = frame[-1], frame.max(), frame.min()
        by_max, by_min = round(100 * (close/_max - 1), 2), round(100 * (close/_min - 1), 2)
        return pd.DataFrame(
            data=[_max, _min, by_max, by_min],
            columns=[self.ticker],
            index=['52H', '52L', 'pct52H', 'pct52L']
        ).T

    def _get_pivot(self) -> pd.DataFrame:
        """ 피벗 지점 """
        if not hasattr(self, '_ohlcv'):
            self._get_ohlcv()
        ohlcv = self.__getattribute__('_ohlcv')

        _, maxima = self.calc_extrema(h=ohlcv.고가, accuracy=2)
        minima, _ = self.calc_extrema(h=ohlcv.저가, accuracy=2)
        return pd.concat(objs={'저점': ohlcv.저가.iloc[minima],'고점': ohlcv.고가.iloc[maxima]}, axis=1)

    def _get_sma(self) -> pd.DataFrame:
        """ 이동 평균선 """
        if not hasattr(self, '_ohlcv'):
            self._get_ohlcv()
        ohlcv, key = self.__getattribute__('_ohlcv'), self.__getattribute__('key')
        return pd.concat(
            objs={f'SMA{win}D': ohlcv[key].rolling(window=win).mean() for win in [5, 10, 20, 60, 120]},
            axis=1
        )

    def _get_ema(self) -> pd.DataFrame:
        """ 지수 이동 평균선 """
        if not hasattr(self, '_ohlcv'):
            self._get_ohlcv()
        ohlcv, key = self.__getattribute__('_ohlcv'), self.__getattribute__('key')
        return pd.concat(
            objs={f'EMA{win}D': ohlcv[key].ewm(span=win).mean() for win in [5, 10, 20, 60, 120]},
            axis=1
        )

    def _get_iir(self) -> pd.DataFrame:
        """ IIR 필터선 """
        if not hasattr(self, '_ohlcv'):
            self._get_ohlcv()
        ohlcv, key = self.__getattribute__('_ohlcv'), self.__getattribute__('key')
        objs, price = dict(), ohlcv[key]
        for win in [5, 10, 20, 60, 120]:
            cutoff = (252 / win) / (252 / 2)
            a, b = butter(N=1, Wn=cutoff)
            objs[f'IIR{win}D'] = pd.Series(data=filtfilt(a, b, price), index=price.index)
        return pd.concat(objs=objs, axis=1)

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


class _trend:
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
        return pd.concat(objs={'resist': hi, 'support': lo}, axis=1)

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
