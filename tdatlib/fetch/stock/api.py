from .fnguide import *
from .timeseries import *
from ta import add_all_ta_features as taf
import numpy as np
np.seterr(divide='ignore', invalid='ignore')


class interface:
    __key = '종가'
    __ohlcv, __rel, __perf, __fiftytwo = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __ta, __namebook = pd.DataFrame(), pd.DataFrame()
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
            self.__perf = getPerformance(ohlcv=self.ohlcv, key=self.__key, name=self.name)
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
    def bollinger(self) -> pd.DataFrame:
        """
        볼린저밴드(Bollinger Band)
        """
        return pd.concat(
            objs={
                'upper': self.ta.volatility_bbh, 'lower': self.ta.volatility_bbl, 'mid': self.ta.volatility_bbm,
                'width': self.ta.volatility_bbw, 'signal': self.ta.volatility_bbp
            }, axis=1
        )

    @property
    def rsi(self) -> pd.Series:
        """
        RSI: Relative Strength Index 데이터프레임
        :return:
        """
        return pd.concat(
            objs={
                'rsi':self.ta.momentum_rsi,
                'stochastic': self.ta.momentum_stoch,
                'stochastic-signal': self.ta.momentum_stoch_signal
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
                'macd': self.ta.trend_macd,
                'signal': self.ta.trend_macd_signal,
                'histogram': self.ta.trend_macd_diff
            }, axis=1
        )