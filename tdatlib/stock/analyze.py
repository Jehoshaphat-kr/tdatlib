from tdatlib import fetch
import math, os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.signal import butter, filtfilt
from scipy.stats import linregress
from ta import add_all_ta_features as lib
from findiff import FinDiff
np.seterr(divide='ignore', invalid='ignore')


class stock(fetch.stock):
    __pivot, __trend, __filters = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    def __init__(self, ticker:str, period:int=5, meta=None):
        super().__init__(ticker=ticker, period=period, meta=meta)
        self.__fillz()

        # Technical Analysis
        # https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#trend-indicators
        if self.exchange == 'krx':
            o, h, l, c, v = '시가', '고가', '저가', '종가', '거래량'
        else:
            o, h, l, c, v = 'open', 'high', 'low', 'close', 'volume'

        try:
            self.__ta = lib(self.ohlcv.copy(), open=o, close=c, low=l, high=h, volume=v)
        except:
            pass
        return

    def __fillz(self):
        """
        거래 중지 이력 Fill Data 전처리
        """
        if self.exchange == 'krx':
            if 0 in self.ohlcv['시가'].tolist():
                p = self.ohlcv.copy()
                data = []
                for o, c, l, h, v in zip(p.시가, p.종가, p.저가, p.고가, p.거래량):
                    if o == 0:
                        data.append([c, c, c, c, v])
                    else:
                        data.append([o, c, l, h, v])
                self.set_ohlcv(
                    ohlcv= pd.DataFrame(data=data, columns=['시가', '종가', '저가', '고가', '거래량'], index=p.index)
                )
        return

    @staticmethod
    def __extrema(h, accuracy=8):
        """
        Customized Pivot Detection
        Originally from PyPI: trendln @https://github.com/GregoryMorse/trendln
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

    @property
    def bb(self) -> pd.DataFrame:
        """
        볼린저(Bollinger) 밴드
        :return:
        """
        return pd.concat(
            objs={
                '상한선': self.__ta.volatility_bbh,
                '하한선': self.__ta.volatility_bbl,
                '기준선': self.__ta.volatility_bbm,
                '밴드폭': self.__ta.volatility_bbw,
                '신호': self.__ta.volatility_bbp
            }, axis=1
        )

    @property
    def macd(self) -> pd.DataFrame:
        """
        MACD: Moving Average Convergence & Divergence 데이터프레임
        :return:
        """
        return pd.concat(
            objs={
                'MACD': self.__ta.trend_macd,
                'MACD-Sig': self.__ta.trend_macd_signal,
                'MACD-Hist': self.__ta.trend_macd_diff
            }, axis=1
        )

    @property
    def stc(self) -> pd.Series:
        """
        STC: Schaff Trend Cycle 데이터프레임
        :return:
        """
        sr = self.__ta.trend_stc
        sr.name = 'STC'
        return sr

    @property
    def cci(self) -> pd.Series:
        """
        CCI: Commodity Channel Index 데이터프레임
        :return:
        """
        sr = self.__ta.trend_cci
        sr.name = 'CCI'
        return sr

    @property
    def trix(self) -> pd.Series:
        """
        TRIX: Triple exponential moving average
        :return:
        """
        sr = self.__ta.trend_trix
        sr.name = 'TRIX'
        return sr

    @property
    def rsi(self) -> pd.Series:
        """
        RSI: Relative Strength Index 데이터프레임
        :return:
        """
        sr = self.__ta.momentum_rsi
        sr.name = 'RSI'
        return sr

    @property
    def s_rsi(self) -> pd.DataFrame:
        """
        Stochastic RSI 데이터프레임
        :return:
        """
        return pd.concat(
            objs={'STOCH-RSI': self.__ta.momentum_stoch, 'STOCH-RSI-Sig': self.__ta.momentum_stoch_signal}, axis=1
        )

    @property
    def vortex(self) -> pd.DataFrame:
        """
        주가 Vortex 데이터프레임
        :return:
        """
        return pd.concat(
            objs={
                'VORTEX(+)': self.__ta.trend_vortex_ind_pos,
                'VORTEX(-)': self.__ta.trend_vortex_ind_neg,
                'VORTEX-Diff': self.__ta.trend_vortex_ind_diff
            }, axis=1
        )

    @property
    def pivot(self) -> pd.DataFrame:
        """
        Pivot 지점 데이터프레임
       :return:
        """
        if self.__pivot.empty:
            price = self.ohlcv[self.ohlcv.index >= (self.ohlcv.index[-1] - timedelta(365))].copy()
            span = price.index

            dump, upper = self.__extrema(h=price['고가'])
            upper_index = [span[n] for n in upper]
            upper_pivot = price[span.isin(upper_index)]['고가']

            lower, dump = self.__extrema(h=price['저가'])
            lower_index = [span[n] for n in lower]
            lower_pivot = price[span.isin(lower_index)]['저가']
            self.__pivot = pd.concat(objs={'고점':upper_pivot, '저점':lower_pivot}, axis=1)
        return self.__pivot

    @property
    def trend(self) -> pd.DataFrame:
        """
        평균 추세선
        :return:
        """
        def norm(frm: pd.DataFrame, period: str, kind: str) -> pd.Series:
            """
            :param frm: 기간 별 slice 가격 및 정수 index N 포함 데이터프레임
            :param period: '1Y', '6M', '3M'
            :param kind: '지지선', '저항선'
            :return:
            """
            is_resist = True if kind == '저항선' else False
            key = '고가' if is_resist else '저가'
            base = frm[key]
            tip_index = base[base == (base.max() if is_resist else base.min())].index[-1]
            right = base[base.index > tip_index].drop_duplicates(keep='last').sort_values(ascending=not is_resist)
            left = base[base.index < tip_index].drop_duplicates(keep='first').sort_values(ascending=not is_resist)

            r_trend = pd.DataFrame()
            l_trend = pd.DataFrame()
            for n, sr in enumerate([right, left]):
                prev_len = len(frm)
                for index in sr.index:
                    sample = frm[frm.index.isin([index, tip_index])][['N', key]]
                    slope, intercept, r_value, p_value, std_err = linregress(sample['N'], sample[key])
                    regress = slope * frm['N'] + intercept

                    curr_len = len(frm[frm[key] >= regress]) if is_resist else len(frm[frm[key] <= regress])
                    if curr_len > prev_len: continue

                    if n:
                        l_trend = slope * frm['N'] + intercept
                    else:
                        r_trend = slope * frm['N'] + intercept

                    if curr_len <= 3:
                        break
                    else:
                        prev_len = curr_len
            if r_trend.empty:
                series = l_trend
            elif l_trend.empty:
                series = r_trend
            else:
                r_e = math.sqrt((r_trend - frm[key]).pow(2).sum())
                l_e = math.sqrt((l_trend - frm[key]).pow(2).sum())
                series = r_trend if r_e < l_e else l_trend
            series.name = f'{period}표준{kind}'
            return series

        def mean(frm_price: pd.DataFrame, frm_pivot: pd.DataFrame, period: str, kind: str) -> pd.Series:
            is_resist = True if kind == '저항선' else False
            key = '고점' if is_resist else '저점'
            y = frm_pivot[key].dropna()
            x = frm_price[frm_price.index.isin(y.index)]['N']
            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            series = slope * frm_price['N'] + intercept
            series.name = f'{period}평균{kind}'
            return series

        if self.__trend.empty:
            objs = []
            gaps = [('1Y', 365), ('6M', 183), ('3M', 91), ('2M', 42)]
            for period, days in gaps:
                on = self.ohlcv.index[-1] - timedelta(days)
                frm_price = self.ohlcv[self.ohlcv.index >= on].copy()
                frm_price['N'] = np.arange(len(frm_price)) + 1
                frm_pivot = self.pivot[self.pivot.index >= on]
                objs.append(mean(frm_price=frm_price, frm_pivot=frm_pivot, period=period, kind='저항선'))
                objs.append(mean(frm_price=frm_price, frm_pivot=frm_pivot, period=period, kind='지지선'))
                objs.append(norm(frm=frm_price, period=period, kind='저항선'))
                objs.append(norm(frm=frm_price, period=period, kind='지지선'))
            self.__trend = pd.concat(objs=objs, axis=1)
        return self.__trend

    @property
    def filters(self) -> pd.DataFrame:
        """
        주가 가이드(필터) 데이터프레임
        :return:
        """
        if self.__filters.empty:
            series = self.ohlcv['종가']
            window = [5, 10, 20, 60, 120]
            # FIR: SMA
            objs = {f'SMA{win}D': series.rolling(window=win).mean() for win in window}

            # FIR: EMA
            objs.update({f'EMA{win}D': series.ewm(span=win).mean() for win in window})
            for win in window:
                # IIR: BUTTERWORTH
                cutoff = (252 / win) / (252 / 2)
                coeff_a, coeff_b = butter(N=1, Wn=cutoff, btype='lowpass', analog=False, output='ba')
                objs[f'IIR{win}D'] = pd.Series(data=filtfilt(coeff_a, coeff_b, series), index=series.index)
            self.__filters = pd.concat(objs=objs, axis=1)
        return self.__filters

    @property
    def guidance(self) -> pd.DataFrame:
        """
        주가 전망 지수 데이터프레임
        :return:
        """
        if self._guidance_.empty:
            combination = [
                ['중장기IIR', 'IIR60D', 'EMA120D'], ['중기IIR', 'IIR60D', 'EMA60D'], ['중단기IIR', 'IIR20D', 'EMA60D'],
                ['중장기SMA', 'SMA60D', 'SMA120D'], ['중단기SMA', 'SMA20D', 'SMA60D'],
                ['중장기EMA', 'EMA60D', 'EMA120D'], ['중단기EMA', 'EMA20D', 'EMA60D']
            ]
            objs = {}
            for label, numerator, denominator in combination:
                basis = self.filters[numerator] - self.filters[denominator]
                objs[label] = basis
                objs[f'd{label}'] = basis.diff()
                objs[f'd2{label}'] = basis.diff().diff()
            self._guidance_ = pd.concat(objs=objs, axis=1)
        return self._guidance_

