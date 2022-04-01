import yfinance as yf
import pandas as pd
import numpy as np
from pykrx import stock as krx
from datetime import datetime, timedelta
from pytz import timezone
from findiff import FinDiff
from scipy.stats import linregress


def getOhlcv(ticker:str, years:int=5) -> pd.DataFrame:
    """
    주가 시계열 데이터
    :param ticker: 중목코드/티커
    :param years: 연단위 기간
                      시가        고가        저가        종가     거래량
    Date
    2017-03-14   49.222000   51.624001   49.203999   51.599998  37992000
    2017-03-15   51.400002   52.200001   50.854000   51.146000  26654000
    2017-03-16   52.480000   53.150002   51.812000   52.410000  35661000
    ...                ...         ...         ...         ...       ...
    2022-03-10  851.450012  854.450012  810.359985  838.299988  19549500
    2022-03-11  840.200012  843.799988  793.770020  795.349976  22272800
    2022-03-14  780.609985  800.699890  756.344971  795.039978   7864541
    """
    curr = datetime.now(timezone('Asia/Seoul' if ticker.isdigit() else 'US/Eastern'))
    prev = curr - timedelta(365 * years)
    if ticker.isdigit() and len(ticker) == 4:
        return krx.get_index_ohlcv_by_date(
            fromdate=prev.strftime("%Y%m%d"),
            todate=curr.strftime("%Y%m%d"),
            ticker=ticker
        )
    elif ticker.isdigit() and not len(ticker) == 4:
        return krx.get_market_ohlcv_by_date(
            fromdate=prev.strftime("%Y%m%d"),
            todate=curr.strftime("%Y%m%d"),
            ticker=ticker
        )
    else:
        o_names = ['Open', 'High', 'Low', 'Close', 'Volume']
        c_names = ['시가', '고가', '저가', '종가', '거래량']
        ohlcv = yf.Ticker(ticker).history(period=f'{years}y')[o_names]
        return ohlcv.rename(columns=dict(zip(o_names, c_names)))

def getRelReturns(ohlcv:pd.DataFrame, key:str='종가') -> pd.DataFrame:
    """
    상대 수익률
    :param ohlcv: 가격
    :param key: 시/고/저/종가
                       3M         6M         1Y          2Y           3Y
    Date
    2019-03-15        NaN        NaN        NaN         NaN     0.000000
    2019-03-18        NaN        NaN        NaN         NaN    -2.156627
    2019-03-19        NaN        NaN        NaN         NaN    -2.890025
    ...               ...        ...        ...         ...          ...
    2022-03-10 -13.256277  12.826378  18.413988  841.761957  1421.802291
    2022-03-11 -17.700562   7.045757  12.347088  793.511106  1343.833273
    2022-03-14 -18.233458   6.352626  11.619630  787.725541  1334.484321
    """
    v = ohlcv[key].copy()
    objs = {
        label: 100 * (v[v.index >= v.index[-1] - timedelta(dt)].pct_change().fillna(0) + 1).cumprod() - 100
        for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095)]
    }
    return pd.concat(objs=objs, axis=1)

def getPerformance(ohlcv:pd.DataFrame, key:str='종가', name:str='기간수익률') -> pd.DataFrame:
    """
    기간별 수익률
    :param ohlcv: 가격
    :param key: 시/고/저/종가
    :param name: 종목명
                 R1D   R1W   R1M   R3M   R6M    R1Y
    SK하이닉스 -0.85 -6.83 -7.94 -4.53  8.92 -17.14
    """
    data = [round(100 * ohlcv[key].pct_change(periods=dt)[-1], 2) for dt in [1, 5, 21, 63, 126, 252]]
    return pd.DataFrame(data=data, columns=[name], index=['R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y']).T

def getFiftyTwo(ohlcv:pd.DataFrame, key:str='종가', name:str='52주대비') -> pd.DataFrame:
    """
    52주 최고/최저 가격 및 대비 수익률
    :param ohlcv: 가격
    :param key: 시/고/저/종가
    :param name: 종목명
                     52H      52L  pct52H  pct52L
    SK하이닉스  144000.0  91500.0  -19.44   26.78
    """
    frame = ohlcv[ohlcv.index >= (ohlcv.index[-1] - timedelta(365))][key]
    close, _max, _min = frame[-1], frame.max(), frame.min()
    by_max, by_min = round(100 * (close/_max - 1), 2), round(100 * (close/_min - 1), 2)
    return pd.DataFrame(
        data=[_max, _min, by_max, by_min],
        columns=[name],
        index=['52H', '52L', 'pct52H', 'pct52L']
    ).T

def getExtrema(h:pd.Series or np.array, accuracy:int=2):
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

def calcAvgTrend(data:pd.Series):
    """
    피벗 데이터 입력 시, 평균 선형 회귀 리턴
    :param data: 피벗 데이터                  :return:
          날짜                                      날짜
    2017-04-04     52200                      2017-04-04     62834.983262
    2017-04-14     50700                      2017-04-14     63143.573207
    2017-05-10     58100                      2017-05-10     63452.163153
                     ...                                              ...
    2022-03-10    121500                      2022-03-10    124861.562337
    2022-03-18    125000                      2022-03-18    125170.152283
    2022-03-30    123000                      2022-03-30    125478.742229
    Name: 고가, Length: 204, dtype: int32     Length: 204, dtype: float64
    """
    data = data.dropna()
    x = np.arange(len(data)) + 1
    slope, intercept, r_value, p_value, std_err = linregress(x, data.values)
    return pd.Series(data=slope * x + intercept, index=data.index)


if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    _ohlcv = getOhlcv(ticker='000660')
    # print(_ohlcv)
    # print(getRelReturns(ohlcv=_ohlcv))
    # print(getPerformance(ohlcv=_ohlcv, name='SK하이닉스'))
    # print(getFiftyTwo(ohlcv=_ohlcv, name='SK하이닉스'))

    _, maxima = getExtrema(h=_ohlcv.고가)
    calc = calcAvgTrend(data=_ohlcv.고가.iloc[maxima])
    print(calc)