from tdatlib.fetch.stock.fnguide import *
from tdatlib.fetch.stock.timeseries import *
from ta import add_all_ta_features as taf
from scipy.signal import butter, filtfilt
np.seterr(divide='ignore', invalid='ignore')


class interface:
    __key = '종가'
    __ohlcv, __rel, __perf, __fiftytwo = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __pivot, __ta, __namebook = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __sma, __ema, __iir, __trend = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), dict()

    __summary, __html1, __html2 = str(), list(), list()
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
        self.__namebook = namebook
        return

    @property
    def name(self) -> str:
        """
        종목명 찾기
        """
        if self.ticker.isalpha():
            return self.ticker
        elif len(self.ticker) == 4:
            return krx.get_index_ticker_name(ticker=self.ticker)
        elif len(self.ticker) == 6:
            if not self.__namebook.empty:
                return self.__namebook.loc[self.ticker, '종목명']
            name = krx.get_market_ticker_name(ticker=self.ticker)
            if isinstance(name, pd.DataFrame):
                return krx.get_etf_ticker_name(ticker=self.ticker)
            return name

    @property
    def currency(self) -> str:
        """
        통화 단위
        """
        return 'USD' if self.ticker.isalpha() else 'KRW'

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
    def ohlcv(self) -> pd.DataFrame:
        """
        가격 정보 시가/고가/저가/종가/거래량
        """
        if self.__ohlcv.empty:
            ohlcv = getOhlcv(ticker=self.ticker, years=self.period)
            if 0 in ohlcv['시가'].tolist():
                prices = zip(ohlcv.시가, ohlcv.종가, ohlcv.저가, ohlcv.고가, ohlcv.거래량)
                data = [[c, c, c, c, v] if o == 0 else [o, c, l, h, v] for o, c, l, h, v in prices]
                self.__ohlcv = pd.DataFrame(data=data, columns=ohlcv.columns, index=ohlcv.index)
            else:
                self.__ohlcv = ohlcv
        return self.__ohlcv

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
            self.__perf = getPerformance(ohlcv=self.ohlcv, key=self.__key, name=self.ticker)
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
                a, b = butter(N=1, Wn=cutoff, btype='lowpass', analog=False, output='ba')
                objs[f'IIR{win}D'] = pd.Series(data=filtfilt(a, b, price), index=price.index)
            self.__iir = pd.concat(objs=objs, axis=1)
        return self.__iir

    def avg_trend(self, gap:str=str()) -> pd.DataFrame:
        """
        평균 추세
        :param gap: 기간
        """
        if not gap in self.__trend.keys():
            self.__trend[gap] = trend(ohlcv=self.ohlcv, pivot=self.pivot, gap=gap)
        t = self.__trend[gap]
        return t.avg

    def bound(self, gap=None):
        """
        기간별 지지선/저항선
        :param gap: 기간
        """
        if not gap in self.__trend.keys():
            self.__trend[gap] = trend(ohlcv=self.ohlcv, pivot=self.pivot, gap=gap)
        t = self.__trend[gap]
        return t.bound

    # -------------------------------------------------------------------------------------------------------------- #

    @property
    def summary(self) -> str:
        """
        기업 개요 Summary (Text)
        """
        if not self.__summary:
            self.__summary = getCorpSummary(ticker=self.ticker)
        return self.__summary

    @property
    def product(self) -> pd.Series:
        """
        제품 구성
        """
        return getProductsPie(ticker=self.ticker)

    @property
    def annual_statement(self) -> pd.DataFrame:
        """
        연간 재무 요약
        """
        if not self.__html1:
            self.__html1 = getMainTables(ticker=self.ticker)
        return getAnnualStatement(ticker=self.ticker, htmls=self.__html1)

    @property
    def quarter_statement(self) -> pd.DataFrame:
        """
        분기 재무 요약
        """
        if not self.__html1:
            self.__html1 = getMainTables(ticker=self.ticker)
        return getQuarterStatement(ticker=self.ticker, htmls=self.__html1)


if __name__ == "__main__":
    t_interface = interface(ticker='005380', period=3)
    print(t_interface.name)
    # print(t_interface.pivot)
    # print(t_interface.bound(gap='2M'))
    # print(t_interface.summary)
    # print(t_interface.product)
    # print(t_interface.annual_statement)
    # print(t_interface.quarter_statement)