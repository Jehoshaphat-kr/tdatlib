from tdatlib.fetch.ohlcv.analysis import *
from ta import add_all_ta_features as taf
from scipy.signal import butter, filtfilt
np.seterr(divide='ignore', invalid='ignore')


class ohlcv:

    __key, __name, __namebook = '종가', str(), pd.DataFrame()
    __ohlcv, __ta = pd.DataFrame(), pd.DataFrame()
    __rel, __perf, __fiftytwo, __pivot = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __sma, __ema, __iir, __trend = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), dict()

    def __init__(self, ticker:str, period:int=5):
        self.ticker, self.period = ticker, period
        return

    def set_key(self, key:str):
        if not key in ['시가', '저가', '고가', '종가']:
            raise KeyError(f"key 값: {key}은 유효하지 않습니다. 입력 가능: ['시가', '저가', '고가', '종가'] ")
        self.__key = key
        self.__rel, self.__perf = pd.DataFrame(), pd.DataFrame()
        return

    def set_namebook(self, namebook:pd.DataFrame):
        self.__namebook = namebook.copy()
        self.__name = str()
        return

    @property
    def name(self) -> str:
        if not self.__name:
            self.__name = getName(ticker=self.ticker, namebook=self.__namebook)
        return self.__name

    @property
    def currency(self) -> str:
        return 'USD' if self.ticker.isalpha() else 'KRW'

    @property
    def ohlcv(self) -> pd.DataFrame:
        """
        가격 정보 시가/고가/저가/종가/거래량
        """
        if self.__ohlcv.empty:
            ohlcv = getOhlcv(ticker=self.ticker, period=self.period)
            if self.currency == 'KRW':
                trade_stop = ohlcv[ohlcv.시가 == 0].copy()
                ohlcv.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop['종가']
                self.__ohlcv = ohlcv
            else:
                self.__ohlcv = ohlcv
        return self.__ohlcv

    @property
    def ta(self) -> pd.DataFrame:
        """
        Technical Analysis
        https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#trend-indicators

       'volume_adi', 'volume_obv', 'volume_cmf', 'volume_fi',
       'volume_em', 'volume_sma_em', 'volume_vpt', 'volume_vwap',
       'volume_mfi', 'volume_nvi',

       'volatility_bbm', 'volatility_bbh',
       'volatility_bbl', 'volatility_bbw', 'volatility_bbp', 'volatility_bbhi',
       'volatility_bbli', 'volatility_kcc', 'volatility_kch', 'volatility_kcl',
       'volatility_kcw', 'volatility_kcp', 'volatility_kchi',
       'volatility_kcli', 'volatility_dcl', 'volatility_dch', 'volatility_dcm',
       'volatility_dcw', 'volatility_dcp', 'volatility_atr', 'volatility_ui',

       'trend_macd', 'trend_macd_signal', 'trend_macd_diff', 'trend_sma_fast',
       'trend_sma_slow', 'trend_ema_fast', 'trend_ema_slow',
       'trend_vortex_ind_pos', 'trend_vortex_ind_neg', 'trend_vortex_ind_diff',
       'trend_trix', 'trend_mass_index', 'trend_dpo', 'trend_kst',
       'trend_kst_sig', 'trend_kst_diff', 'trend_ichimoku_conv',
       'trend_ichimoku_base', 'trend_ichimoku_a', 'trend_ichimoku_b',
       'trend_stc', 'trend_adx', 'trend_adx_pos', 'trend_adx_neg', 'trend_cci',
       'trend_visual_ichimoku_a', 'trend_visual_ichimoku_b', 'trend_aroon_up',
       'trend_aroon_down', 'trend_aroon_ind', 'trend_psar_up',
       'trend_psar_down', 'trend_psar_up_indicator',
       'trend_psar_down_indicator',

       'momentum_rsi', 'momentum_stoch_rsi',
       'momentum_stoch_rsi_k', 'momentum_stoch_rsi_d', 'momentum_tsi',
       'momentum_uo', 'momentum_stoch', 'momentum_stoch_signal', 'momentum_wr',
       'momentum_ao', 'momentum_roc', 'momentum_ppo', 'momentum_ppo_signal',
       'momentum_ppo_hist', 'momentum_kama', 'others_dr', 'others_dlr',
       'others_cr'
        """
        if self.__ta.empty:
            o, h, l, c, v = '시가', '고가', '저가', '종가', '거래량'
            if len(self.ohlcv) > 20:
                self.__ta = taf(self.ohlcv.copy(), open=o, close=c, low=l, high=h, volume=v)
        return self.__ta

    @property
    def rel(self) -> pd.DataFrame:
        """
        기간별 상대 수익률 (시계열, 벤치마크X)
        """
        if self.__rel.empty:
            self.__rel = getRelReturns(ohlcv=self.ohlcv, key=self.__key)
        return self.__rel

    @property
    def perf(self) -> pd.DataFrame:
        """
        기간별 수익률
        """
        if self.__perf.empty:
            self.__perf = getPerf(ohlcv=self.ohlcv, key=self.__key, name=self.ticker)
        return self.__perf

    @property
    def fiftytwo(self) -> pd.DataFrame:
        """
        52주 가격 및 대비 수익률
        """
        if self.__fiftytwo.empty:
            self.__fiftytwo = getFiftyTwo(ohlcv=self.ohlcv, key=self.__key, name=self.name)
        return self.__fiftytwo

    @property
    def pivot(self) -> pd.DataFrame:
        """
        가격 피벗 지점
        """
        if self.__pivot.empty:
            _, maxima = getExtrema(h=self.ohlcv.고가, accuracy=2)
            minima, _ = getExtrema(h=self.ohlcv.저가, accuracy=2)
            self.__pivot = pd.concat(
                objs={
                    '저점': self.ohlcv.저가.iloc[minima],
                    '고점': self.ohlcv.고가.iloc[maxima]
                }, axis=1
            )
        return self.__pivot

    @property
    def sma(self) -> pd.DataFrame:
        """
        Simple Moving Average
        """
        if self.__sma.empty:
            self.__sma = pd.concat(
                objs={f'SMA{win}D': self.ohlcv[self.__key].rolling(window=win).mean() for win in [5, 10, 20, 60, 120]},
                axis=1
            )
        return self.__sma

    @property
    def ema(self) -> pd.DataFrame:
        """
        Exponential Moving Average
        """
        if self.__ema.empty:
            self.__ema = pd.concat(
                objs={f'EMA{win}D': self.ohlcv[self.__key].ewm(span=win).mean() for win in [5, 10, 20, 60, 120]},
                axis=1
            )
        return self.__ema

    @property
    def iir(self) -> pd.DataFrame:
        """
        Infinite-Impulse Response Filter: 반응 조정형(BUTTERWORTH)
        """
        if self.__iir.empty:
            objs, price = dict(), self.ohlcv[self.__key]
            for win in [5, 10, 20, 60, 120]:
                cutoff = (252 / win) / (252 / 2)
                a, b = butter(N=1, Wn=cutoff)
                objs[f'IIR{win}D'] = pd.Series(data=filtfilt(a, b, price), index=price.index)
            self.__iir = pd.concat(objs=objs, axis=1)
        return self.__iir

    def get_trend(self, gap: str = str()) -> pd.DataFrame:
        """
        평균 추세
        :param gap: 기간
        """
        if not gap in self.__trend.keys():
            self.__trend[gap] = trend(ohlcv=self.ohlcv, pivot=self.pivot, gap=gap)
        t = self.__trend[gap]
        return t.avg

    def get_bound(self, gap: str = str()):
        """
        기간별 지지선/저항선
        :param gap: 기간
        """
        if not gap in self.__trend.keys():
            self.__trend[gap] = trend(ohlcv=self.ohlcv, pivot=self.pivot, gap=gap)
        t = self.__trend[gap]
        return t.bound


if __name__ == "__main__":
    ticker = '035720'
    # ticker = '1028'
    # ticker = 'TSLA'

    app = ohlcv(ticker=ticker, period=3)
    print(app.ohlcv)
    print(app.perf)
    # print(app.rel)
    # print(app.pivot)
    # print(app.sma)
    # print(app.ema)
    # print(app.iir)
    # print(app.get_trend(gap='3M'))
    # print(app.get_bound(gap='3M'))