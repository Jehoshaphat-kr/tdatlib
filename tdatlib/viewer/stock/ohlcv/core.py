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
