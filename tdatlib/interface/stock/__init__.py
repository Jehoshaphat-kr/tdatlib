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
    calc_trend,
    calc_trix_sign
)
from tdatlib.interface.stock.value import (
    calc_asset,
    calc_profit
)
import pandas as pd


class interface_stock(fetch_stock):

    def __calc__(self, p: str, fname: str = str(), **kwargs):
        if not hasattr(self, f'__{p}'):
            self.__setattr__(f'__{p}', globals()[f"calc_{fname if fname else p}"](**kwargs))
        return self.__getattribute__(f'__{p}')

    @property
    def ta(self) -> pd.DataFrame:
        """
        Technical Analysis
        :return:
                     시가   고가   저가  ...  others_dr  others_dlr  others_cr
        날짜                             ...
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
        상대 수익률
        :return:
                          3M        6M         1Y         2Y        3Y         5Y
        날짜
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
        시계열 낙폭
        :return:
                          3M        6M         1Y         2Y         3Y         5Y
        날짜
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
        이동 평균선
        :return:
                      SMA5D   SMA10D   SMA20D        SMA60D       SMA120D
        날짜
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
        지수 이동 평균선
        :return:
                           EMA5D        EMA10D  ...        EMA60D       EMA120D
        날짜                                      ...
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
        IIR 필터선
        :return:
                           IIR5D        IIR10D  ...        IIR60D       IIR120D
        날짜                                      ...
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
        기간별 수익률
        :return:

                 R1D   R1W   R1M   R3M   R6M    R1Y
        253450  1.74  1.96  4.69  8.82  6.23 -13.15
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def cagr(self) -> pd.DataFrame:
        """
        3M / 6M / 1Y / 2Y / 3Y / 5Y 연평균화 수익률
        :return:

                   3M     6M     1Y    2Y    3Y    5Y
        253450  38.55  11.05 -10.67  5.17 -1.21  5.49
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def volatility(self) -> pd.DataFrame:
        """
        3M / 6M / 1Y / 2Y / 3Y / 5Y 연평균화 변동성
        :return:

                   3M     6M    1Y     2Y     3Y    5Y
        253450  33.99  32.32  28.3  30.07  35.68  40.4
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def fiftytwo(self) -> pd.DataFrame:
        """
        52주 최고/최저 가격 및 대비 수익률
        :return:

                   52H    52L  pct52H  pct52L
        253450  106400  73100  -11.84   28.32
        """
        return self.__calc__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def avg_trend(self) -> pd.DataFrame:
        """
        2M / 3M / 6M / 1Y 평균 추세
        :return:

                              2M            3M            6M            1Y
        날짜
        2021-04-19           NaN           NaN           NaN  28269.707532
        2021-04-20           NaN           NaN           NaN  28250.902293
        2021-04-21           NaN           NaN           NaN  28232.097054
        ...                  ...           ...           ...           ...
        2022-04-14  23415.377697  23319.884209  22555.336484  21499.821449
        2022-04-15  23436.252573  23335.154925  22549.787845  21481.016210
        2022-04-18  23498.877202  23380.967073  22533.141929  21424.600493
        """
        return self.__calc__(inner().f_code.co_name, fname='trend', ohlcv=self.ohlcv).avg

    @property
    def avg_slope(self) -> dict:
        """
        2M / 3M / 6M / 1Y 평균 추세선 고가 기울기
        :return: 

        {'2M': 90.5241935483871, '3M': 115.84006512618194, '6M': -1.67125418860699, '1Y': -21.830711400644308}
        """
        return self.__calc__(inner().f_code.co_name, fname='trend', ohlcv=self.ohlcv).avg_slope

    @property
    def bnd_trend(self) -> pd.DataFrame:
        """
        2M / 3M / 6M / 1Y 지지선 추세선 (고, 저가 기준)
        :return:

                                       2M  ...                           1Y
                          resist  support  ...         resist       support
        날짜                               ...
        2021-04-15           NaN      NaN  ...  107100.000000  90009.316770
        2021-04-16           NaN      NaN  ...  107065.564738  89947.826087
        2021-04-19           NaN      NaN  ...  106962.258953  89763.354037
        ...                  ...      ...  ...            ...           ...
        2022-04-13  94600.000000  88150.0  ...   94600.000000  67688.198758
        2022-04-14  94648.484848  88300.0  ...   94565.564738  67626.708075
        2022-04-15  94696.969697  88450.0  ...   94531.129477  67565.217391
        """
        return self.__calc__(inner().f_code.co_name, fname='trend', ohlcv=self.ohlcv).bound

    @property
    def asset(self) -> pd.DataFrame:
        """
        연간 자산, 부채, 자본 총계 (단위: 억원)
        :return:

                   자산총계  부채총계  자본총계    자산총계LB  부채총계LB  자본총계LB
        2017/12        4595       910      3684      4595억원     910억원    3684억원
        2018/12        5124      1111      4013      5124억원    1111억원    4013억원
        2019/12        5816      1533      4283      5816억원    1533억원    4283억원
        2020/12        7573      1480      6093      7573억원    1480억원    6093억원
        2021/12        8840      2002      6839      8840억원    2002억원    6839억원
        2022/12(E)     9393      2023      7370      9393억원    2023억원    7370억원
        2023/12(E)    10352      2178      8174  1조 0352억원    2178억원    8174억원
        2024/12(E)    11755      2298      9457  1조 1755억원    2298억원    9457억원
        """
        return self.__calc__(inner().f_code.co_name, df_statement=self.annual_stat)

    @property
    def profit(self) -> pd.DataFrame:
        """
        매출, 영업이익, 당기순이익 (단위: 억원)
        :return:

                  매출액  영업이익  당기순이익  매출액LB  영업이익LB  당기순이익LB
        2017/12     2868       330         238  2868억원     330억원       238억원
        2018/12     3796       399         358  3796억원     399억원       358억원
        2019/12     4687       287         264  4687억원     287억원       264억원
        2020/12     5257       491         296  5257억원     491억원       296억원
        2021/12     4871       526         390  4871억원     526억원       390억원
        2022/12(E)  6429       832         623  6429억원     832억원       623억원
        2023/12(E)  7324       996         745  7324억원     996억원       745억원
        2024/12(E)  7822      1247         964  7822억원    1247억원       964억원
        """
        return self.__calc__(inner().f_code.co_name, df_statement=self.annual_stat)

    @property
    def trix_sign(self) -> pd.DataFrame:
        """
        TRIX 지표 기준 매매 신호 감지
        :return:

                      Signal    Bottom
        날짜
        2017-04-19       NaN       NaN
        ...              ...       ...
        2022-02-21 -0.004991       NaN
        2022-02-25       NaN  0.047175
        2022-03-07  0.003213       NaN
        2022-03-18       NaN -0.100612
        2022-03-29 -0.005523       NaN
        """
        return self.__calc__(inner().f_code.co_name, ta=self.ta)


if __name__ == "__main__":
    # t_ticker = 'TSLA'
    t_ticker = '001680'

    tester = interface_stock(ticker=t_ticker)
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
    # print(tester.bnd_trend)
    # print(tester.asset)
    # print(tester.profit)
    print(tester.trix_sign)