from tdatlib.fetch.archive.deprecate.ohlcv._ohlcv import _ohlcv, _trend
from inspect import currentframe as inner
import pandas as pd


class ohlcv(_ohlcv):

    def __init__(self, ticker:str, period:int=5, key:str='종가', namebook:pd.DataFrame=pd.DataFrame()):
        super().__init__(ticker=ticker, period=period, key=key, namebook=namebook)
        return

    def __checkattr__(self, name:str) -> str:
        if not hasattr(self, f'__{name}'):
            _func = self.__getattribute__(f'_get_{name}')
            self.__setattr__(f'__{name}', _func())
        return f'__{name}'

    def set_key(self, key:str):
        """ key값 변경 """
        if not key in ['시가', '저가', '고가', '종가']:
            raise KeyError
        self.key = key
        self.__delattr__('__relative_return')
        return

    @property
    def name(self) -> str:
        """ 종목명 """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def currency(self) -> str:
        """ 통화 단위 """
        return 'USD' if self.ticker.isalpha() else 'KRW'

    @property
    def ohlcv(self) -> pd.DataFrame:
        """
        가격 정보 시가/고가/저가/종가/거래량
        :return:
                      시가    고가    저가    종가   거래량
        날짜
        2019-04-09   20473   20473   20071   20172   383038
        2019-04-10   20272   20673   20172   20573   263334
        2019-04-11   20673   20673   20372   20573   253796
        ...            ...     ...     ...     ...      ...
        2022-04-06  105500  106500  104000  105000  1529617
        2022-04-07  103000  103500   99900   99900  2885845
        2022-04-08  100000  100500   97100   97300  1517817
        """
        return self._ohlcv

    @property
    def ta(self) -> pd.DataFrame:
        """
        Technical Analysis
        https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#trend-indicators

       'volume_adi', 'volume_obv', 'volume_cmf', 'volume_fi', 'volume_em', 'volume_sma_em', 'volume_vpt',
       'volume_vwap', 'volume_mfi', 'volume_nvi',

       'volatility_bbm', 'volatility_bbh', 'volatility_bbl', 'volatility_bbw', 'volatility_bbp', 'volatility_bbhi',
       'volatility_bbli', 'volatility_kcc', 'volatility_kch', 'volatility_kcl', 'volatility_kcw', 'volatility_kcp',
       'volatility_kchi', 'volatility_kcli', 'volatility_dcl', 'volatility_dch', 'volatility_dcm', 'volatility_dcw',
       'volatility_dcp', 'volatility_atr', 'volatility_ui',

       'trend_macd', 'trend_macd_signal', 'trend_macd_diff', 'trend_sma_fast', 'trend_sma_slow', 'trend_ema_fast',
       'trend_ema_slow', 'trend_vortex_ind_pos', 'trend_vortex_ind_neg', 'trend_vortex_ind_diff', 'trend_trix',
       'trend_mass_index', 'trend_dpo', 'trend_kst', 'trend_kst_sig', 'trend_kst_diff', 'trend_ichimoku_conv',
       'trend_ichimoku_base', 'trend_ichimoku_a', 'trend_ichimoku_b', 'trend_stc', 'trend_adx', 'trend_adx_pos',
       'trend_adx_neg', 'trend_cci', 'trend_visual_ichimoku_a', 'trend_visual_ichimoku_b', 'trend_aroon_up',
       'trend_aroon_down', 'trend_aroon_ind', 'trend_psar_up', 'trend_psar_down', 'trend_psar_up_indicator',
       'trend_psar_down_indicator',

       'momentum_rsi', 'momentum_stoch_rsi', 'momentum_stoch_rsi_k', 'momentum_stoch_rsi_d', 'momentum_tsi',
       'momentum_uo', 'momentum_stoch', 'momentum_stoch_signal', 'momentum_wr', 'momentum_ao', 'momentum_roc',
       'momentum_ppo', 'momentum_ppo_signal', 'momentum_ppo_hist', 'momentum_kama', 'others_dr', 'others_dlr',
       'others_cr'
        """
        if len(self.ohlcv) <= 20:
            raise ReferenceError(f'{self.name}({self.ticker}) length is below 20.')
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def relative_return(self) -> pd.DataFrame:
        """
        시계열 상대 수익률
        :return:
                     3M         6M         1Y          2Y          3Y          5Y
        날짜
        2019-04-09  NaN        NaN        NaN         NaN    0.000000    0.000000
        2019-04-10  NaN        NaN        NaN         NaN    1.987904    1.987904
        2019-04-11  NaN        NaN        NaN         NaN    1.987904    1.987904
        ...         ...        ...        ...         ...         ...         ...
        2022-04-06  5.0 -12.133891  -4.538512  231.094504  420.523498  420.523498
        2022-04-07 -0.1 -16.401674  -9.175213  215.012771  395.240928  395.240928
        2022-04-08 -2.9 -18.744770 -11.720852  206.183584  381.360301  381.360301
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def drawdown(self) -> pd.DataFrame:
        """
        시계열 낙폭
        :return:
                          3M         6M         1Y         2Y         3Y         5Y
        날짜
        2019-04-09       NaN        NaN        NaN        NaN   0.000000   0.000000
        2019-04-10       NaN        NaN        NaN        NaN   0.000000   0.000000
        2019-04-11       NaN        NaN        NaN        NaN   0.000000   0.000000
        ...              ...        ...        ...        ...        ...        ...
        2022-04-06 -3.225806 -19.230769 -38.053097 -38.053097 -38.053097 -38.053097
        2022-04-07 -7.926267 -23.153846 -41.061947 -41.061947 -41.061947 -41.061947
        2022-04-08 -9.677419 -24.615385 -42.182891 -42.182891 -42.182891 -42.182891
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def perf(self) -> pd.DataFrame:
        """
        기간별 수익률
        :return:
                R1D  R1W  R1M    R3M    R6M   R1Y
        035720 -2.8 -8.4 -2.9 -12.91 -12.52 -3.05
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def fiftytwo(self) -> pd.DataFrame:
        """
        52주 가격 및 대비 수익률
        :return:
                     52H      52L  pct52H  pct52L
        035720  169500.0  82600.0  -42.77   17.43
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def pivot(self) -> pd.DataFrame:
        """
        고/저점 피벗
        :return:
                          저점     고점
        날짜
        2019-04-10       NaN   20673.0
        2019-04-18       NaN   23983.0
        2019-04-19   23081.0       NaN
        ...              ...       ...
        2022-03-30       NaN  108000.0
        2022-04-04  104000.0       NaN
        2022-04-05       NaN  108000.0
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def sma(self) -> pd.DataFrame:
        """
        이동 평균선
        :return:
                       SMA5D    SMA10D    SMA20D        SMA60D        SMA120D
        날짜
        2019-04-09       NaN       NaN       NaN           NaN            NaN
        2019-04-10       NaN       NaN       NaN           NaN            NaN
        2019-04-11       NaN       NaN       NaN           NaN            NaN
        ...              ...       ...       ...           ...            ...
        2022-04-06  106100.0  105750.0  105125.0  96043.333333  109042.500000
        2022-04-07  104780.0  105240.0  105120.0  96041.666667  108900.000000
        2022-04-08  102980.0  104440.0  104895.0  95991.666667  108695.833333
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def ema(self) -> pd.DataFrame:
        """
        지수 이동 평균선
        :return:
                            EMA5D         EMA10D  ...         EMA60D        EMA120D
        날짜                                        ...
        2019-04-09   20172.000000   20172.000000  ...   20172.000000   20172.000000
        2019-04-10   20412.600000   20392.550000  ...   20375.841667   20374.170833
        2019-04-11   20488.578947   20465.089701  ...   20443.763726   20441.554871
        ...                   ...            ...  ...            ...            ...
        2022-04-06  105922.401394  105624.752249  ...  102239.662010  107419.829099
        2022-04-07  103914.934263  104583.888204  ...  102162.951780  107295.533865
        2022-04-08  101609.956175  103204.999439  ...  101993.674673  107125.359027
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def iir(self) -> pd.DataFrame:
        """
        Infinite-Impulse Response Filter: 반응 조정형(BUTTERWORTH)
        :return:
                            IIR5D         IIR10D  ...         IIR60D       IIR120D
        날짜                                        ...
        2019-04-09   20171.999172   20171.183818  ...   20350.155891  20585.714808
        2019-04-10   20451.424350   20511.387923  ...   20618.116655  20756.449706
        2019-04-11   20635.478325   20869.834379  ...   20887.678860  20927.963272
        ...                   ...            ...  ...            ...           ...
        2022-04-06  104004.452804  102585.000283  ...   99545.463195  99104.652456
        2022-04-07  100498.864533   99964.669830  ...   99062.635938  98966.873400
        2022-04-08   97100.001699   97103.394156  ...   98564.249289  98824.955002
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    def get_trend(self, gap: str = str()) -> pd.DataFrame:
        """
        기간 내 평균 직선 추세
        :param gap: 기간
        :return:
                          support         resist
        날짜
        2022-01-06   81523.386164   87977.053862
        2022-01-07   81753.561918   88199.209023
        2022-01-10   82444.089181   88865.674506
        ...                   ...            ...
        2022-04-06  102239.204055  107971.018341
        2022-04-07  102469.379809  108193.173502
        2022-04-08  102699.555564  108415.328663
        """
        if not hasattr(self, f'trend_{gap}'):
            self.__setattr__(f'trend_{gap}', _trend(ohlcv=self.ohlcv, pivot=self.pivot, gap=gap))
        return self.__getattribute__(f'trend_{gap}').avg

    def get_bound(self, gap: str = str()):
        """
        기간 내 지지선/저항선
        :param gap: 기간
        :return:
                           resist       support
        날짜
        2022-01-06  103000.000000  78025.641026
        2022-01-07  103094.594595  78215.384615
        2022-01-10  103378.378378  78784.615385
        ...                   ...           ...
        2022-04-06  111513.513514  95102.564103
        2022-04-07  111608.108108  95292.307692
        2022-04-08  111702.702703  95482.051282
        """
        if not hasattr(self, f'trend_{gap}'):
            self.__setattr__(f'trend_{gap}', _trend(ohlcv=self.ohlcv, pivot=self.pivot, gap=gap))
        return self.__getattribute__(f'trend_{gap}').bound

    def cagr(self, days:int=-1):
        """ CAGR """
        return self._get_cagr(days=days)

    def volatility(self, days:int=-1):
        """ Volatility """
        return self._get_volatility(days=days)

    def sharpe_ratio(self, days:int=-1):
        """ Sharpe Ratio """
        return round(self.cagr(days=days) / self.volatility(days=days), 2)


if __name__ == "__main__":
    ticker = '005930'
    # ticker = '1028'
    # ticker = 'TSLA'

    app = ohlcv(ticker=ticker, period=5)
    print(app.name)

    # print(app.ohlcv)
    # print(app.ta)
    # print(app.sma)
    # print(app.ema)
    # print(app.iir)
    print(app.relative_return)
    # print(app.drawdown)
    # print(app.perf)
    # print(app.fiftytwo)
    # print(app.cagr())
    # print(app.cagr(days=365 * 2))
    # print(app.cagr(days=365))
    # print(app.cagr(days=183))
    # print(app.volatility())
    # print(app.pivot)
    # print(app.get_bound(gap='3M'))
    # print(app.get_trend(gap='3M'))