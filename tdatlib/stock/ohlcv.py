from tdatlib.dataset.tools.tool import (
    fit,
    delimit
)
from pykrx.stock import (
    get_index_ticker_name,
    get_market_ticker_name,
    get_etf_ticker_name
)
from datetime import datetime, timedelta
from pytz import timezone
from pykrx import stock
from ta import add_all_ta_features
from scipy.signal import butter, filtfilt
from inspect import currentframe as inner
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
    df = pd.concat(objs=objs, axis=1)

    for col in df.columns:
        tr = df[col].dropna()
        dx, dy = (tr.index[-1] - tr.index[0]).days, 100 * (tr[-1] / tr[0] - 1)
        slope = round(dy / dx, 2)
        df[f'{col}-Slope'] = slope
    return df


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



class technical(object):

    def __init__(self, ticker: str, period: int = 5, endate: str = str()):
        self.ticker = ticker
        self.period = period
        self.endate = datetime.strptime(endate, "%Y%m%d") if endate else endate

        """
        주가/지수 정보 기본 수집

                     시가   고가   저가   종가  거래량
        날짜
        2017-05-10  22000  22250  21300  21450  878239
        2017-05-11  21450  22000  21300  21450  853057
        2017-05-12  21450  21600  21250  21350  339716
        ...           ...    ...    ...    ...     ...
        2022-05-03  67700  68400  67200  67700  363237
        2022-05-04  68000  68200  67600  67900  252004
        2022-05-06  66700  67200  65700  66200  639829
        """
        self.__raw = fetch_ohlcv(ticker=ticker, period=period)
        self.ohlcv = self.__raw[self.__raw.index <= self.endate].copy() if endate else self.__raw.copy()
        return

    def __ref__(self, p: str, fname: str = str(), **kwargs):
        _p = p.replace('ohlcv_', '')
        if not hasattr(self, f'__{_p}'):
            self.__setattr__(f'__{_p}', globals()[f"{fname if fname else 'calc'}_{_p}"](**kwargs))
        return self.__getattribute__(f'__{_p}')

    @property
    def label(self) -> str:
        if not hasattr(self, '__name'):
            if self.ticker.isdigit() and len(self.ticker) == 4:
                self.__setattr__('__name', get_index_ticker_name(ticker=self.ticker))
            elif self.ticker.isdigit() and len(self.ticker) == 6:
                name = get_market_ticker_name(ticker=self.ticker)
                if isinstance(name, pd.DataFrame):
                    self.__setattr__('__name', get_etf_ticker_name(ticker=self.ticker))
                self.__setattr__('__name', name)
            else:
                self.__setattr__('__name', self.ticker)
        return self.__getattribute__('__name')

    @label.setter
    def label(self, name):
        self.__setattr__('__name', name)
        return

    @property
    def currency(self) -> str:
        if self.ticker.isdigit() and len(self.ticker) == 6:
            return '원'
        elif self.ticker.isdigit() and len(self.ticker) == 4:
            return '-'
        else:
            return 'USD'

    @property
    def ohlcv_btr(self) -> pd.DataFrame:
        """
        Back Test Right-side
        :return: endate 이후 20TD 정답 데이터

                     시가   고가   저가   종가   거래량  등락   누적  최대  최소
        날짜
        2021-05-10  55800  59100  55800  59000  1094299  0.00   0.00  9.32 -8.78
        2021-05-11  57500  58300  55800  55800  1276832 -5.42  -5.42  9.32 -8.78
        2021-05-12  55800  58400  55000  57900  1421123  3.76  -1.86  9.32 -8.78
        ...           ...    ...    ...    ...      ...   ...    ...   ...   ...
        2021-06-03  54700  57300  54100  56600  2568573  5.20  -4.07  9.32 -8.78
        2021-06-04  56100  58300  55200  57500  1909271  1.59  -2.54  9.32 -8.78
        2021-06-07  58300  58800  56000  56500  1241930 -1.74  -4.24  9.32 -8.78
        """
        ohlcv_ans = self.__raw[self.__raw.index > self.endate] if self.endate else pd.DataFrame()
        return self.__ref__(inner().f_code.co_name, ohlcv_ans=ohlcv_ans)

    @property
    def ohlcv_btl(self) -> pd.DataFrame:
        """
        Back Test Left-side
        :return:
                     시가   고가   저가   종가  거래량   최대   최소
        날짜
        2017-05-15  21300  21700  21150  21600  487892   7.57 -11.47
        2017-05-16  21800  21800  20650  20800  778107  13.29  -6.76
        2017-05-17  20700  20900  20450  20650  572898  15.23  -5.16
        ...           ...    ...    ...    ...     ...    ...    ...
        2021-05-04  55100  55700  52700  55400  716587    NaN    NaN
        2021-05-06  54700  55600  54300  55400  518715    NaN    NaN
        2021-05-07  55700  56300  54900  55700  442683    NaN    NaN
        """
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def ohlcv_returns(self) -> pd.DataFrame:
        """
        :return:

                R1D   R1W   R1M    R3M    R6M    R1Y
        000990 -2.5 -1.49 -5.83 -10.54  12.97  17.79
        """
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def ohlcv_ta(self) -> pd.DataFrame:
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
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def ohlcv_rr(self) -> pd.DataFrame:
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
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def ohlcv_dd(self) -> pd.DataFrame:
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
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def ohlcv_sma(self) -> pd.DataFrame:
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
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def ohlcv_ema(self) -> pd.DataFrame:
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
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def ohlcv_iir(self) -> pd.DataFrame:
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
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def ohlcv_cagr(self) -> pd.DataFrame:
        """
        3M / 6M / 1Y / 2Y / 3Y / 5Y 연평균화 수익률
        :return:

                   3M     6M     1Y    2Y    3Y    5Y
        253450  38.55  11.05 -10.67  5.17 -1.21  5.49
        """
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def ohlcv_volatility(self) -> pd.DataFrame:
        """
        3M / 6M / 1Y / 2Y / 3Y / 5Y 연평균화 변동성
        :return:

                   3M     6M    1Y     2Y     3Y    5Y
        253450  33.99  32.32  28.3  30.07  35.68  40.4
        """
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def ohlcv_fiftytwo(self) -> pd.DataFrame:
        """
        52주 최고/최저 가격 및 대비 수익률
        :return:

                   52H    52L  pct52H  pct52L
        253450  106400  73100  -11.84   28.32
        """
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

    @property
    def ohlcv_trend(self) -> pd.DataFrame:
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
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def ohlcv_bound(self) -> pd.DataFrame:
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
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv)

    @property
    def ohlcv_bband(self) -> bband:
        """
        볼린저 밴드 객체
        :return:
        """
        if not hasattr(self, '__bband'):
            self.__setattr__('__bband', bband(parent=self))
        return self.__getattribute__('__bband')


if __name__ == "__main__":
    tech = technical(ticker='000990', endate='20210509')

    # print(tech.ohlcv)
    # print(tech.ohlcv_bt)
    # print(tech.ohlcv_btr)
    # print(tech.ohlcv_returns)
    # print(tech.ohlcv_ta)
    # print(tech.ohlcv_rr)
    # print(tech.ohlcv_dd)
    # print(tech.ohlcv_sma)
    # print(tech.ohlcv_ema)
    # print(tech.ohlcv_iir)
    # print(tech.ohlcv_cagr)
    # print(tech.ohlcv_volatility)
    # print(tech.ohlcv_fiftytwo)
    # print(tech.ohlcv_trend)
    # print(tech.ohlcv_bound)