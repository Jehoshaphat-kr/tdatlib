from inspect import currentframe as inner
from tdatlib.fetch.stock import fetch_stock
from tdatlib.interface.stock.ohlcv import (
    calc_ta,
    calc_rr,
    calc_dd,
    calc_volatility,
    calc_sma,
    calc_ema,
    calc_iir,
    calc_cagr,
    calc_perf,
    calc_fiftytwo,
    calc_avg_trend,
    calc_bound,
    calc_backtest_return
)
from tdatlib.interface.stock.value import (
    calc_asset,
    calc_profit
)
import pandas as pd


def ta_cols() -> pd.DataFrame:
    from tdatlib.fetch.archive import root
    return pd.read_csv(f'{root}/tacols.csv', encoding='utf-8').fillna('x')


class interface_stock(fetch_stock):

    def __calc__(self, p: str, fname: str = str(), **kwargs):
        if not hasattr(self, f'__{p}'):
            self.__setattr__(f'__{p}', globals()[f"calc_{fname if fname else p}"](**kwargs))
        return self.__getattribute__(f'__{p}')

    @property
    def ohlcv(self) -> pd.DataFrame:
        if not hasattr(self, '__ohlcv'):
            self.__setattr__(
                '__ohlcv',
                self.ohlcv_raw[self.ohlcv_raw.index <= self.endate] if self.endate else self.ohlcv_raw
            )
        return self.__getattribute__('__ohlcv')

    @property
    def ohlcv_ans(self) -> pd.DataFrame:
        if not hasattr(self, '__ohlcv_ans'):
            self.__setattr__(
                '__ohlcv_ans',
                self.ohlcv_raw[self.ohlcv_raw.index > self.endate] if self.endate else pd.DataFrame()
            )
        return self.__getattribute__('__ohlcv_ans')

    @property
    def ta(self) -> pd.DataFrame:
        """
        Technical Analysis
        volume          volatility        trend                       momentum               others
        -------------   ---------------   -------------------------   --------------------   --------
        volume_adi      volatility_bbm    trend_macd                  momentum_rsi           others_dr
        volume_obv      volatility_bbh    trend_macd_signal           momentum_stoch_rsi     others_dlr
        volume_cmf      volatility_bbl    trend_macd_diff             momentum_stoch_rsi_k   others_cr
        volume_fi       volatility_bbw    trend_sma_fast              momentum_stoch_rsi_d
        volume_em       volatility_bbp    trend_sma_slow              momentum_tsi
        volume_sma_em   volatility_bbhi   trend_ema_fast              momentum_uo
        volume_vpt      volatility_bbli   trend_ema_slow              momentum_stoch
        volume_vwap     volatility_kcc    trend_vortex_ind_pos        momentum_stoch_signal
        volume_mfi      volatility_kch    trend_vortex_ind_neg        momentum_wr
        volume_nvi      volatility_kcl    trend_vortex_ind_diff       momentum_ao
                        volatility_kcw    trend_trix                  momentum_roc
                        volatility_kcp    trend_mass_index            momentum_ppo
                        volatility_kchi   trend_dpo                   momentum_ppo_signal
                        volatility_kcli   trend_kst                   momentum_ppo_hist
                        volatility_dcl    trend_kst_sig               momentum_pvo
                        volatility_dch    trend_kst_diff              momentum_pvo_signal
                        volatility_dcm    trend_ichimoku_conv         momentum_pvo_hist
                        volatility_dcw    trend_ichimoku_base         momentum_kama
                        volatility_dcp    trend_ichimoku_a
                        volatility_atr    trend_ichimoku_b
                        volatility_ui     trend_stc
                                          trend_adx
                                          trend_adx_pos
                                          trend_adx_neg
                                          trend_cci
                                          trend_visual_ichimoku_a
                                          trend_visual_ichimoku_b
                                          trend_aroon_up
                                          trend_aroon_down
                                          trend_aroon_ind
                                          trend_psar_up
                                          trend_psar_down
                                          trend_psar_up_indicator
                                          trend_psar_down_indicator

        :return:
                     ??????   ??????   ??????  ...  others_dr  others_dlr  others_cr
        ??????                             ...
        2017-11-24  55300  71800  55300  ... -17.601842         NaN   0.000000
        2017-11-27  75000  81300  69900  ...  -0.696379   -0.698815  -0.696379
        2017-11-28  70700  70700  64000  ... -10.238429  -10.801324 -10.863510
        ...           ...    ...    ...  ...        ...         ...        ...
        2022-04-13  91100  94600  90200  ...   4.070407    3.989747  31.754875
        2022-04-14  94000  94400  92200  ...  -2.536998   -2.569735  28.412256
        2022-04-15  91900  94400  91300  ...   1.735358    1.720473  30.640669
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def rr(self) -> pd.DataFrame:
        """
        ?????? ?????????
        :return:
                          3M        6M         1Y         2Y        3Y         5Y
        ??????
        2017-11-24       NaN       NaN        NaN        NaN       NaN   0.000000
        2017-11-27       NaN       NaN        NaN        NaN       NaN  -0.696379
        2017-11-28       NaN       NaN        NaN        NaN       NaN -10.863510
        ...              ...       ...        ...        ...       ...        ...
        2022-04-13  9.490741  6.292135  -9.904762  11.556604 -2.774923  31.754875
        2022-04-14  6.712963  3.595506 -12.190476   8.726415 -5.241521  28.412256
        2022-04-15  8.564815  5.393258 -10.666667  10.613208 -3.597122  30.640669
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def dd(self) -> pd.DataFrame:
        """
        ????????? ??????
        :return:
                          3M        6M         1Y         2Y         3Y         5Y
        ??????
        2017-11-24       NaN       NaN        NaN        NaN        NaN   0.000000
        2017-11-27       NaN       NaN        NaN        NaN        NaN  -0.696379
        2017-11-28       NaN       NaN        NaN        NaN        NaN -10.863510
        ...              ...       ...        ...        ...        ...        ...
        2022-04-13  0.000000 -1.867220 -11.090226 -13.369963 -13.369963 -21.035058
        2022-04-14 -2.536998 -4.356846 -13.345865 -15.567766 -15.567766 -23.038397
        2022-04-15 -0.845666 -2.697095 -11.842105 -14.102564 -14.102564 -21.702838
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def sma(self) -> pd.DataFrame:
        """
        ?????? ?????????
        :return:
                      SMA5D   SMA10D   SMA20D        SMA60D       SMA120D
        ??????
        2017-11-24      NaN      NaN      NaN           NaN           NaN
        2017-11-27      NaN      NaN      NaN           NaN           NaN
        2017-11-28      NaN      NaN      NaN           NaN           NaN
        ...             ...      ...      ...           ...           ...
        2022-04-13  91380.0  91440.0  90830.0  86293.333333  87751.666667
        2022-04-14  91980.0  91460.0  90960.0  86390.000000  87728.333333
        2022-04-15  92340.0  91620.0  91120.0  86506.666667  87719.166667
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def ema(self) -> pd.DataFrame:
        """
        ?????? ?????? ?????????
        :return:
                           EMA5D        EMA10D  ...        EMA60D       EMA120D
        ??????                                      ...
        2017-11-24  71800.000000  71800.000000  ...  71800.000000  71800.000000
        2017-11-27  71500.000000  71525.000000  ...  71545.833333  71547.916667
        2017-11-28  67947.368421  68500.000000  ...  68946.254976  68989.896067
        ...                  ...           ...  ...           ...           ...
        2022-04-13  92048.881317  91487.537789  ...  88540.789539  88317.762059
        2022-04-14  92099.254211  91617.076373  ...  88660.763653  88381.931282
        2022-04-15  92666.169474  92013.971578  ...  88829.263205  88471.486139
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def iir(self) -> pd.DataFrame:
        """
        IIR ?????????
        :return:
                           IIR5D        IIR10D  ...        IIR60D       IIR120D
        ??????                                      ...
        2017-11-24  71799.993997  71783.727338  ...  71495.776545  72817.721773
        2017-11-27  69364.605830  69450.918497  ...  70757.643268  72495.913987
        2017-11-28  65876.502931  67047.722919  ...  70032.263237  72182.054594
        ...                  ...           ...  ...           ...           ...
        2022-04-13  92894.342040  92683.429119  ...  92362.753969  90894.502633
        2022-04-14  93245.477295  93231.598171  ...  92543.162110  90977.154385
        2022-04-15  93799.993197  93794.685856  ...  92716.334156  91053.705110
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def perf(self) -> pd.DataFrame:
        """
        ????????? ?????????
        :return:

                 R1D   R1W   R1M   R3M   R6M    R1Y
        253450  1.74  1.96  4.69  8.82  6.23 -13.15
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def cagr(self) -> pd.DataFrame:
        """
        3M / 6M / 1Y / 2Y / 3Y / 5Y ???????????? ?????????
        :return:

                   3M     6M     1Y    2Y    3Y    5Y
        253450  38.55  11.05 -10.67  5.17 -1.21  5.49
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def volatility(self) -> pd.DataFrame:
        """
        3M / 6M / 1Y / 2Y / 3Y / 5Y ???????????? ?????????
        :return:

                   3M     6M    1Y     2Y     3Y    5Y
        253450  33.99  32.32  28.3  30.07  35.68  40.4
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def fiftytwo(self) -> pd.DataFrame:
        """
        52??? ??????/?????? ?????? ??? ?????? ?????????
        :return:

                   52H    52L  pct52H  pct52L
        253450  106400  73100  -11.84   28.32
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def avg_trend(self) -> pd.DataFrame:
        """
        2M / 3M / 6M / 1Y ?????? ??????
        :return:

                              2M            3M            6M            1Y
        ??????
        2021-04-19           NaN           NaN           NaN  28269.707532
        2021-04-20           NaN           NaN           NaN  28250.902293
        2021-04-21           NaN           NaN           NaN  28232.097054
        ...                  ...           ...           ...           ...
        2022-04-14  23415.377697  23319.884209  22555.336484  21499.821449
        2022-04-15  23436.252573  23335.154925  22549.787845  21481.016210
        2022-04-18  23498.877202  23380.967073  22533.141929  21424.600493
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def bound(self) -> pd.DataFrame:
        """
        2M / 3M / 6M / 1Y ????????? ????????? (???, ?????? ??????)
        :return:

                                       2M  ...                           1Y
                          resist  support  ...         resist       support
        ??????                               ...
        2021-04-15           NaN      NaN  ...  107100.000000  90009.316770
        2021-04-16           NaN      NaN  ...  107065.564738  89947.826087
        2021-04-19           NaN      NaN  ...  106962.258953  89763.354037
        ...                  ...      ...  ...            ...           ...
        2022-04-13  94600.000000  88150.0  ...   94600.000000  67688.198758
        2022-04-14  94648.484848  88300.0  ...   94565.564738  67626.708075
        2022-04-15  94696.969697  88450.0  ...   94531.129477  67565.217391
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def asset(self) -> pd.DataFrame:
        """
        ?????? ??????, ??????, ?????? ?????? (??????: ??????)
        :return:

                   ????????????  ????????????  ????????????    ????????????LB  ????????????LB  ????????????LB
        2017/12        4595       910      3684      4595??????     910??????    3684??????
        2018/12        5124      1111      4013      5124??????    1111??????    4013??????
        2019/12        5816      1533      4283      5816??????    1533??????    4283??????
        2020/12        7573      1480      6093      7573??????    1480??????    6093??????
        2021/12        8840      2002      6839      8840??????    2002??????    6839??????
        2022/12(E)     9393      2023      7370      9393??????    2023??????    7370??????
        2023/12(E)    10352      2178      8174  1??? 0352??????    2178??????    8174??????
        2024/12(E)    11755      2298      9457  1??? 1755??????    2298??????    9457??????
        """
        return self.__calc__(inner().f_code.co_name, df_statement=self.annual_stat)

    @property
    def profit(self) -> pd.DataFrame:
        """
        ??????, ????????????, ??????????????? (??????: ??????)
        :return:

                  ?????????  ????????????  ???????????????  ?????????LB  ????????????LB  ???????????????LB
        2017/12     2868       330         238  2868??????     330??????       238??????
        2018/12     3796       399         358  3796??????     399??????       358??????
        2019/12     4687       287         264  4687??????     287??????       264??????
        2020/12     5257       491         296  5257??????     491??????       296??????
        2021/12     4871       526         390  4871??????     526??????       390??????
        2022/12(E)  6429       832         623  6429??????     832??????       623??????
        2023/12(E)  7324       996         745  7324??????     996??????       745??????
        2024/12(E)  7822      1247         964  7822??????    1247??????       964??????
        """
        return self.__calc__(inner().f_code.co_name, df_statement=self.annual_stat)

    @property
    def backtest_return(self) -> pd.DataFrame:
        """
        ???????????? ?????? ?????????
        :return:

                     ??????   ??????   ??????   ??????   ?????????  ??????   ??????   ??????  ??????
        ??????
        2021-05-03  25950  26150  25500  25900   181123  0.00   0.00  20.42 -1.73
        2021-05-04  25950  26600  25950  26500   502744  2.32   2.32  20.42 -1.73
        2021-05-06  26500  27250  26500  27200   598690  2.64   5.02  20.42 -1.73

        2021-05-28  29650  29950  29200  29550   301501 -0.17  14.09  20.42 -1.73
        2021-05-31  29550  30200  29300  29900   376981  1.18  15.44  20.42 -1.73
        2021-06-01  30050  30400  29500  29500   238375 -1.34  13.90  20.42 -1.73
        """
        return self.__calc__(inner().f_code.co_name, ohlcv_ans=self.ohlcv_ans)


if __name__ == "__main__":
    # t_ticker = 'TSLA'
    t_ticker = '001680'

    # print(ta_cols())

    tester = interface_stock(ticker=t_ticker, endate='20210430')
    # tester = interface_stock(ticker=t_ticker)

    # print(tester.ohlcv)
    # print(tester.ta)
    # print(tester.rr)
    # print(tester.dd)
    # print(tester.sma)
    # print(tester.ema)
    # print(tester.iir)
    # print(tester.perf)
    # print(tester.cagr)
    # print(tester.volatility)
    # print(tester.fiftytwo)
    # print(tester.avg_trend)
    # print(tester.avg_slope)
    # print(tester.bound)
    # print(tester.asset)
    # print(tester.profit)
    # print(tester.trix_sign)
    # print(tester.ta.columns)
    print(tester.backtest_return)
