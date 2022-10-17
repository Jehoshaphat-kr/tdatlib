import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta


def price_generalize(ohlcv:pd.DataFrame) -> pd.Series:
    if not ('종가' in ohlcv.columns and '고가' in ohlcv.columns and '저가' in ohlcv.columns):
        raise KeyError
    return (1/3) * ohlcv.종가 + (1/3) * ohlcv.고가 + (1/3) * ohlcv.저가


def rsquared(l:pd.Series, r:pd.Series) -> float:
    matrix = pd.concat(objs=[l, r], axis=1).corr(method='pearson', min_periods=1)
    print(matrix)
    corr = matrix.iloc[1, 0]
    return 100 * (-1 if corr < 0 else 1) * corr ** 2


def rsquared_rolling(l:pd.Series, r:pd.Series, win:int=126) -> pd.DataFrame:
    index = np.arange(start=-win, stop=win + 1, step=1)
    dates = [l.index[-1] + timedelta(int(i)) for i in index]
    data = [[rsquared(l, r.shift(i)), i] for i in index]
    return pd.DataFrame(data=data, index=dates, columns=['R-Square', 'TD'])


class corr(object):

    __window = 126
    def __init__(self, l:pd.Series, r:pd.Series):
        self.__l, self.__r = l.copy(), r.copy()
        return

    @property
    def window(self) -> int:
        return self.__window

    @window.setter
    def window(self, window:int):
        self.__window = window

    @property
    def rsquare(self) -> float:
        return rsquared(self.__l, self.__r)

    @property
    def rolling_rsquare(self) -> pd.Series:
        if not hasattr(self, f'_rolling_rsquare'):
            self.__setattr__(f'_rolling_rsquare', rsquared_rolling(self.__l, self.__r, self.window))
        return self.__getattribute__(f'_rolling_rsquare')

    def display(self):
        rr = self.rolling_rsquare
        fig = make_subplots(
            rows=2, cols=1, row_width=[0.3, 0.7], vertical_spacing=0.02, shared_xaxes=False,
            specs=[
                [{"type": "xy", "secondary_y": True}],
                [{"type": "xy"}]
            ]

        )
        fig.add_trace(go.Scatter(
            x=self.__l.index, y=self.__l, name='Left',
            xhoverformat='%Y/%m/%d', hovertemplate='%{x}<br>%{y}<extra></extra>'
        ), row=1, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(
            x=self.__r.index, y=self.__r, name='right',
            xhoverformat='%Y/%m/%d', hovertemplate='%{x}<br>%{y}<extra></extra>'
        ), row=1, col=1, secondary_y=True)

        fig.add_trace(go.Scatter(
            x=rr['TD'], y=rr['R-Square'], visible=True, showlegend=False,
            hovertemplate='%{x}TD<br>%{y:.2f}<extra></extra>'
        ), row=2, col=1)

        fig.update_layout(
            plot_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='lightgrey'),
            yaxis=dict(showgrid=True, gridcolor='lightgrey'),
            xaxis2=dict(showgrid=True, gridcolor='lightgrey', zeroline=True, zerolinecolor='lightgrey'),
            yaxis3=dict(showgrid=True, gridcolor='lightgrey', zeroline=True, zerolinecolor='lightgrey'),
            xaxis_rangeslider=dict(visible=False)
        )
        fig.show()
        return




# def coincidence(series_x_2:pd.DataFrame, win:int=126) -> int:
#     rolled_r_square = r_square_rolling(series_x_2, win=win)
#     best = max(rolled_r_square.abs())
#     i_prev = rolled_r_square[rolled_r_square == best].index[0]
#     i_curr = rolled_r_square.index[-1]
#     return (i_curr - i_prev).days


if __name__ == "__main__":
    from tdatlib import stock, macro

    period = 20
    macro = macro.ecos()
    stock = stock.kr(ticker='105560')
    macro.period = stock.period = period

    exchange = price_generalize(macro.원달러환율)
    price = price_generalize(stock.ohlcv)

    corr = corr(price, exchange)
    print(corr.rsquare)
    # print(corr.rolling_rsquare)
    # corr.display()