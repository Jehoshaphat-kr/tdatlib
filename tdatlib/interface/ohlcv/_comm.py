import pandas as pd


PM_KEY = '종가'

def calc_perf(ticker_ohlcv:list or tuple) -> pd.DataFrame:
    """
    기간별 수익률
    :return:
    """
    ticker, ohlcv = ticker_ohlcv
    data = [round(100 * ohlcv[PM_KEY].pct_change(periods=dt)[-1], 2) for dt in [1, 5, 21, 63, 126, 252]]
    return pd.DataFrame(data=data, columns=[ticker], index=['R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y']).T