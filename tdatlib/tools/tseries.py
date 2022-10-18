import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta


def price_generalize(ohlcv:pd.DataFrame) -> pd.Series:
    if not ('종가' in ohlcv.columns and '고가' in ohlcv.columns and '저가' in ohlcv.columns):
        raise KeyError
    return (1/3) * ohlcv.종가 + (1/3) * ohlcv.고가 + (1/3) * ohlcv.저가


def corr(l:pd.Series, r:pd.Series) -> float:
    # l = (l - l.min()) / (l.max() - l.min())
    # r = (r - r.min()) / (r.max() - r.min())
    df = pd.concat(objs=[l, r], axis=1)
    df = df[df.index.isin(l.index)]
    matrix_t = df.corr(method='pearson', min_periods=1)
    matrix_dt = pd.concat(objs=[l.diff(), r.diff()], axis=1).corr(method='pearson', min_periods=1)
    matrix_dt = 0
    return 0.5 * matrix_t.iloc[0, 1]# + 0.5 * matrix_dt.iloc[0, 1]


def corr_rolling(l:pd.Series, r:pd.Series, month:int) -> pd.DataFrame:
    prev_day = l.index[-1] - timedelta(days=int(month * 30.5))
    samples = len(r.index[r.index >= prev_day])
    index = np.arange(start=-samples, stop=samples + 1, step=1)

    dates = [r.index[-1] + timedelta(int(i)) for i in index]
    data = [[corr(l, r.shift(i)), i] for i in index]
    return pd.DataFrame(data=data, index=dates, columns=['corrcoef', 'days'])


class rel(object):

    __month = 6
    def __init__(self, l:pd.Series, r:pd.Series):
        self.__l, self.__r = l.copy(), r.copy()
        self.__l_dtype = ':,d' if str(l.dtype).startswith('int') else ':.2f'
        self.__r_dtype = ':,d' if str(r.dtype).startswith('int') else ':.2f'
        return

    @property
    def month(self) -> int:
        return self.__month

    @month.setter
    def month(self, month:int):
        self.__month = month

    @property
    def corr(self) -> float:
        return corr(self.__l, self.__r)

    @property
    def rolling_corr(self) -> pd.Series:
        if not hasattr(self, f'_rolling_corr'):
            self.__setattr__(f'_rolling_corr', corr_rolling(self.__l, self.__r, self.month))
        return self.__getattribute__(f'_rolling_corr')

    def display(self):
        rr = self.rolling_corr
        fig = make_subplots(
            rows=2, cols=1, row_width=[0.3, 0.7], vertical_spacing=0.02, shared_xaxes=False,
            specs=[
                [{"type": "xy", "secondary_y": True}],
                [{"type": "xy"}]
            ]

        )
        fig.add_trace(go.Scatter(
            x=self.__l.index, y=self.__l, name='Left',
            xhoverformat='%Y/%m/%d', hovertemplate='%{x}<br>%{y' + f'{self.__l_dtype}' + '}<extra></extra>'
        ), row=1, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(
            x=self.__r.index, y=self.__r, name='right',
            xhoverformat='%Y/%m/%d', hovertemplate='%{x}<br>%{y' + f'{self.__r_dtype}' + '}<extra></extra>'
        ), row=1, col=1, secondary_y=True)

        fig.add_trace(go.Scatter(
            x=rr['days'], y=rr['corrcoef'], visible=True, showlegend=False,
            hovertemplate='%{x}TD<br>%{y:.4f}<extra></extra>'
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
    from tdatlib import stock, macro, market

    period = 20

    macro = macro.ecos()
    index = market.index()
    stock = stock.kr(ticker='105560')
    # stock = stock.kr(ticker='005930')
    macro.period = index.period = stock.period = period

    # exchange = price_generalize(macro.원달러환율)
    # price = price_generalize(stock.ohlcv)
    kospi = index.kospi.종가
    exchange = macro.원달러환율.종가
    price = stock.ohlcv.종가

    # relation = rel(price, kospi)
    relation = rel(price, exchange)
    print(relation.corr)
    print(relation.rolling_corr)
    # relation.display()