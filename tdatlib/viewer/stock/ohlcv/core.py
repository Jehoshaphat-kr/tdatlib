from tdatlib.dataset.stock.ohlcv import technical
from tdatlib.viewer.tools import CD_RANGER, save
from tdatlib.dataset import tools
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


class objs(technical):

    def obj_candle(self) -> go.Candlestick:
        if not hasattr(self, '__candle'):
            self.__setattr__(
                '__candle',
                go.Candlestick(
                    name='캔들 차트',
                    x=self.ohlcv.index,
                    open=self.ohlcv.시가,
                    high=self.ohlcv.고가,
                    low=self.ohlcv.저가,
                    close=self.ohlcv.종가,
                    visible=True,
                    showlegend=True,
                    legendgrouptitle=dict(text='캔들 차트'),
                    increasing_line=dict(color='red'),
                    decreasing_line=dict(color='royalblue'),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',' if self.currency == '원' else '.2f',
                )
            )
        return self.__getattribute__('__candle')

    def obj_volume(self) -> go.Bar:
        if not hasattr(self, f'__volume'):
            self.__setattr__(
                f'__volume',
                go.Bar(
                    name='거래량',
                    x=self.ohlcv.index,
                    y=self.ohlcv.거래량,
                    marker=dict(color=self.ohlcv.거래량.pct_change().apply(lambda x: 'blue' if x < 0 else 'red')),
                    visible=True,
                    showlegend=False,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',',
                    hovertemplate='%{x}<br>거래량: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__(f'__volume')

    def obj_price(self, col:str) -> go.Scatter:
        if not hasattr(self, f'__{col}'):
            self.__setattr__(
                f'__{col}',
                go.Scatter(
                    name=col,
                    x=self.ohlcv.index,
                    y=self.ohlcv[col],
                    visible='legendonly',
                    showlegend=True,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',' if self.currency == '원' else '.2f',
                    legendgrouptitle=dict(text='주가 차트') if col == '시가' else None,
                    hovertemplate='%{x}<br>' + col + ': %{y}' + self.currency + '<extra></extra>'
                )
            )
        return self.__getattribute__(f'__{col}')

    def obj_ma(self, col:str) -> go.Scatter:
        if not hasattr(self, f'__{col}'):
            self.__setattr__(
                f'__{col}',
                go.Scatter(
                    name=col,
                    x=self.ohlcv_sma.index,
                    y=self.ohlcv_sma[col],
                    visible='legendonly' if col in ['MA5D', 'MA10D', 'MA20D'] else True,
                    showlegend=True,
                    legendgrouptitle=dict(text='이동 평균선') if col == 'MA5D' else None,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',.0f',
                    hovertemplate='%{x}<br>' + col + ': %{y}' + self.currency + '<extra></extra>'
                )
            )
        return self.__getattribute__(f'__{col}')

    def obj_nc(self, col:str) -> go.Scatter:
        if not hasattr(self, f'__{col}'):
            self.__setattr__(
                f'__{col}',
                go.Scatter(
                    name=col,
                    x=self.ohlcv_iir.index,
                    y=self.ohlcv_iir[col],
                    visible='legendonly',
                    showlegend=True,
                    legendgrouptitle=dict(text='노이즈 제거선') if col == 'NC5D' else None,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',.0f',
                    hovertemplate='%{x}<br>' + col + ': %{y}' + self.currency + '<extra></extra>'
                )
            )
        return self.__getattribute__(f'__{col}')

    def obj_trend(self, col:str) -> go.Scatter:
        if not hasattr(self, f'__tr{col}'):
            tr = self.ohlcv_trend[col].dropna()
            dx, dy = (tr.index[-1] - tr.index[0]).days, 100 * (tr[-1] / tr[0] - 1)
            slope = round(dy / dx, 2)
            self.__setattr__(
                f'__tr{col}',
                go.Scatter(
                    name=col.replace('M', '개월').replace('Y', '년'),
                    x=tr.index,
                    y=tr,
                    mode='lines',
                    line=dict(
                        width=2,
                        dash='dot'
                    ),
                    visible='legendonly',
                    showlegend=True,
                    legendgrouptitle=dict(text='평균 추세선') if col == '1M' else None,
                    hovertemplate=f'{col} 평균 추세 강도: {slope}[%/days]<extra></extra>'
                )
            )
        return self.__getattribute__(f'__tr{col}')

    def obj_bound(self, col:str) -> tuple:
        if not hasattr(self, f'__bd{col}'):
            name = col.replace('M', '개월').replace('Y', '년')
            self.__setattr__(
                f'__bd{col}',
                (
                    go.Scatter(
                        name=f'{name}',
                        x=self.ohlcv_bound.index,
                        y=self.ohlcv_bound[col].resist,
                        mode='lines',
                        visible='legendonly',
                        showlegend=True,
                        legendgroup=col,
                        legendgrouptitle=dict(text='지지/저항선') if col == '2M' else None,
                        line=dict(dash='dot', color='blue'),
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',.0f',
                        hovertemplate='%{x}<br>저항: %{y}' + self.currency + '<extra></extra>'
                    ),
                    go.Scatter(
                        name=f'{name}',
                        x=self.ohlcv_bound.index,
                        y=self.ohlcv_bound[col].support,
                        mode='lines',
                        visible='legendonly',
                        showlegend=False,
                        legendgroup=col,
                        line=dict(dash='dot', color='red'),
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',.0f',
                        hovertemplate='%{x}<br>지지: %{y}' + self.currency + '<extra></extra>'
                    )
                )
            )
        return self.__getattribute__(f'__bd{col}')


class sketch(object):

    def __init__(self):
        self.__x_axis = dict(
            showticklabels=False,
            tickformat='%Y/%m/%d',
            zeroline=False,
            showgrid=True,
            gridcolor='lightgrey',
            autorange=True,
            showline=True,
            linewidth=1,
            linecolor='grey',
            mirror=False,
        )

    def x_axis(self, title:str=str()) -> dict:
        _ = self.__x_axis
        _['title'] = title
        return _

    def x_axis_rangeselector(self, title:str) -> dict:
        _ = self.xaxis(title=title)
        _['rangeselector'] = CD_RANGER
        return _

