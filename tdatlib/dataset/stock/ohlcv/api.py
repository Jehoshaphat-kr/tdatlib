from tdatlib.dataset.stock.ohlcv.common import (
    fetch_ohlcv,
    calc_ohlcv_bt,
    calc_returns,
    calc_ta,
    calc_rr,
    calc_dd,
    calc_sma,
    calc_ema,

)
from inspect import currentframe as inner
from datetime import datetime
import pandas as pd


class technical(object):

    def __init__(self, ticker:str, period:int=5, endate:str=str()):
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

    def __ref__(self, p:str, fname:str=str(), **kwargs):
        if not hasattr(self, f'__{p}'):
            self.__setattr__(f'__{p}', globals()[f"{fname if fname else 'calc'}_{p}"](**kwargs))
        return self.__getattribute__(f'__{p}')

    @property
    def ohlcv_bt(self) -> pd.DataFrame:
        """
        :return:

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
        return self.__ref__(
            inner().f_code.co_name,
            ohlcv_ans=self.__raw[self.__raw.index > self.endate] if self.endate else pd.DataFrame()
        )

    @property
    def returns(self) -> pd.DataFrame:
        """
        :return:

                R1D   R1W   R1M    R3M    R6M    R1Y
        000990 -2.5 -1.49 -5.83 -10.54  12.97  17.79
        """
        return self.__ref__(inner().f_code.co_name, ohlcv=self.ohlcv, ticker=self.ticker)

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


if __name__ == "__main__":

    tech = technical(ticker='000990', endate='20210509')

    print(tech.ohlcv)
    print(tech.ohlcv_bt)
    print(tech.returns)
    print(tech.ta)