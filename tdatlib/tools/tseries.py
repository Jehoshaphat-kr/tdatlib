import pandas as pd


def price_generalize(price:pd.DataFrame) -> pd.Series:
    if not ('종가' in price.columns and '고가' in price.columns and '저가' in price.columns):
        raise KeyError
    return (1/3) * price.종가 + (1/3) * price.고가 + (1/3) * price.저가


def r_square(series_x_2:pd.DataFrame) -> float:
    if not len(series_x_2.columns) == 2:
        raise KeyError('2 Sets of time series correlation argument needed')

    matrix = series_x_2.corr(method='pearson', min_periods=1)
    corr = matrix.iloc[1, 0]
    return 100 * (-1 if corr < 0 else 1) * corr ** 2


def r_square_rolling(series_x_2:pd.DataFrame, win:int=126) -> pd.Series:
    comparee = series_x_2[series_x_2.columns[0]]
    comparer = series_x_2[series_x_2.columns[1]]

    r_squared = [r_square(pd.concat([comparee, comparer.shift(-i)], axis=1)) for i in range(-win+1, 1, 1)]
    return pd.Series(index=comparer.index[-win:], data=r_squared)


def coincidence(series_x_2:pd.DataFrame, win:int=126) -> int:
    rolled_r_square = r_square_rolling(series_x_2, win=win)
    best = max(rolled_r_square.abs())
    i_prev = rolled_r_square[rolled_r_square == best].index[0]
    i_curr = rolled_r_square.index[-1]
    return (i_curr - i_prev).days


if __name__ == "__main__":
    from tdatlib import stock


    stock = stock.kr(ticker='005960')
    t_price = stock.ohlcv

    # print(t_price)
    # print(price_generalize(t_price))
    # t_r_square = r_square(t_price[['시가', '종가']])
    # print(t_r_square)

    # t_r_square_rolling = r_square_rolling(t_price[['시가', '종가']])
    # print(t_r_square_rolling)

    t_concidence = coincidence(t_price[['시가', '종가']])
    print(t_concidence)