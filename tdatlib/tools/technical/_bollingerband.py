from tdatlib.tools.tracer import (
    draw_line,
    draw_bar,
    draw_candle,
)
from tdatlib.tools.technical._series import zc
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import numpy as np


class _default(object):
    __col = "TP"  # [str] 시가, 종가, 고가, 저가 또는 TP(Typical Price)
    __win = 20  # [int] 이동 평균 개수
    __std = 2  # [int, float] 상/하한 표준 편차 범위 가중치
    __rec = False # [bool] recession trace 추가 여부
    __key = f"{__col}_{__win}_{__std}"

    def __init__(self, ohlcv: pd.DataFrame, name: str = str(), unit: str = str()):
        self.ohlcv = ohlcv
        self.name = name if name else ohlcv.name
        self.curr = unit if unit else ''
        return

    @property
    def key(self) -> str:
        return self.__key

    @property
    def col(self) -> str:
        return self.__col

    @col.setter
    def col(self, col: str):
        self.__col = col

    @property
    def window(self) -> int:
        return self.__win

    @window.setter
    def window(self, window: int):
        self.__win = window

    @property
    def std(self) -> str:
        return self.__std

    @std.setter
    def std(self, std: int or float):
        self.__std = std

    @property
    def recession(self) -> bool:
        return self.__rec

    @recession.setter
    def recession(self, on:bool):
        self.__rec = on

    @property
    def basis(self) -> pd.Series:
        attr = f'__basis_{self.key}'
        if not hasattr(self, attr):
            if self.__col == "TP":
                self.__setattr__(attr, (self.ohlcv.고가 + self.ohlcv.저가 + self.ohlcv.종가) / 3)
            else:
                self.__setattr__(attr, self.ohlcv[self.__col])
        return self.__getattribute__(attr)

    @property
    def middle(self) -> pd.Series:
        attr = f'__middle_{self.key}'
        if not hasattr(self, attr):
            _t = self.basis.rolling(window=self.window).mean()
            self.__setattr__(attr, _t)
        return self.__getattribute__(attr)

    @property
    def upper_edge(self) -> pd.Series:
        attr = f'__upper_edge_{self.key}'
        if not hasattr(self, attr):
            _t = self.middle + self.__std * self.basis.rolling(window=self.window).std()
            self.__setattr__(attr, _t)
        return self.__getattribute__(attr)

    @property
    def lower_edge(self) -> pd.Series:
        attr = f'__lower_edge_{self.key}'
        if not hasattr(self, attr):
            _t = self.middle - self.__std * self.basis.rolling(window=self.window).std()
            self.__setattr__(attr, _t)
        return self.__getattribute__(attr)

    @property
    def upper_trend(self) -> pd.Series:
        attr = f'__upper_trend_{self.key}'
        if not hasattr(self, attr):
            _t = self.middle + (self.__std/2) * self.basis.rolling(window=self.window).std()
            self.__setattr__(attr, _t)
        return self.__getattribute__(attr)

    @property
    def lower_trend(self) -> pd.Series:
        attr = f'__lower_trend_{self.key}'
        if not hasattr(self, attr):
            _t = self.middle - (self.__std/2) * self.basis.rolling(window=self.window).std()
            self.__setattr__(attr, _t)
        return self.__getattribute__(attr)


    @property
    def width(self) -> pd.Series:
        attr = f'__width_{self.key}'
        if not hasattr(self, attr):
            _t = ((self.upper_edge - self.lower_edge) / self.middle) * 100
            self.__setattr__(attr, _t)
        return self.__getattribute__(attr)

    @property
    def pctb(self) -> pd.Series:
        attr = f'__pctb_{self.key}'
        if not hasattr(self, attr):
            _t = (self.basis - self.lower_edge) / (self.upper_edge - self.lower_edge).where(
                self.upper_edge != self.lower_edge, np.nan
            )
            self.__setattr__(attr, _t)
        return self.__getattribute__(attr)



class _analytic(_default):

    @property
    def traditional_signal(self) -> pd.DataFrame:
        attr = f'__t_sig_{self.key}'
        if not hasattr(self, attr):
            sell, buy, prev = list(), list(), 0
            for date, curr in self.pctb.dropna().items():
                if prev > 1 > curr:
                    sell.append(date)
                if prev < 0 < curr:
                    buy.append(date)
                prev = curr
            _t = pd.concat(
                objs=dict(sell=self.ohlcv.loc[sell, '종가'], buy=self.ohlcv.loc[buy, '종가']),
                axis=1
            )
            self.__setattr__(attr, _t)
        return self.__getattribute__(attr)


class _traces(_analytic):

    @property
    def trace_upper_edge(self) -> go.Scatter:
        return go.Scatter(
            name="볼린저밴드", x=self.upper_edge.index, y=self.upper_edge, visible=True,
            mode='lines', line=dict(color='rgb(197, 224, 180)'), fill=None,
            showlegend=True, legendgroup="bb",
            xhoverformat="%Y/%m/%d", yhoverformat=",.2f",
            hovertemplate="%{x}<br>상단: %{y}" + self.curr + "<extra></extra>"
        )

    @property
    def trace_upper_trend(self):
        return go.Scatter(
            x=self.upper_trend.index, y=self.upper_trend, visible=True,
            mode='lines', line=dict(color='rgb(197, 224, 180)', width=0), fill='tonexty',
            showlegend=False, legendgroup='bb',
            xhoverformat="%Y/%m/%d", yhoverformat=",.2f",
            hovertemplate="%{x}<br>%{y}" + self.curr + "<extra></extra>"
        )

    @property
    def trace_middle(self) -> go.Scatter:
        return go.Scatter(
            x=self.middle.index, y=self.middle, visible=True,
            mode='lines', line=dict(color='rgb(255, 242, 204)'), fill='tonexty',
            showlegend=False, legendgroup="bb",
            xhoverformat="%Y/%m/%d", yhoverformat=",.2f",
            hovertemplate="%{x}<br>MA: %{y}" + self.curr + "<extra></extra>"
        )

    @property
    def trace_lower_trend(self):
        return go.Scatter(
            x=self.lower_trend.index, y=self.lower_trend, visible=True,
            mode='lines', line=dict(color='rgb(255, 242, 204)', width=0), fill='tonexty',
            showlegend=False, legendgroup='bb',
            xhoverformat="%Y/%m/%d", yhoverformat=",.2f",
            hovertemplate="%{x}<br>%{y}" + self.curr + "<extra></extra>"
        )

    @property
    def trace_lower_edge(self) -> go.Scatter:
        return go.Scatter(
            x=self.lower_edge.index, y=self.lower_edge, visible=True,
            mode='lines', line=dict(color='rgb(248, 203, 173)'), fill='tonexty',
            showlegend=False, legendgroup="bb",
            xhoverformat="%Y/%m/%d", yhoverformat=",.2f",
            hovertemplate="%{x}<br>하단: %{y}" + self.curr + "<extra></extra>"
        )

    @property
    def trace_width(self) -> go.Scatter:
        _t = draw_line(data=self.width, name="밴드폭")
        return _t

    @property
    def trace_pctb(self) -> go.Scatter:
        _t = draw_line(data=self.pctb, name="밴드%B")
        return _t

    @property
    def trace_traditional_sell(self) -> go.Scatter:
        sell = self.traditional_signal.sell.dropna()
        return go.Scatter(
            name="[T] Sell", x=sell.index, y=sell, visible='legendonly',
            mode='markers', marker=dict(symbol='triangle-down', color='red', size=8),
            xhoverformat="%Y/%m/%d", yhoverformat=",.2f", hovertemplate="%{x}<br>%{y}" + self.curr + "<extra>Sell</extra>"
        )

    @property
    def trace_traditional_buy(self) -> go.Scatter:
        buy = self.traditional_signal.buy.dropna()
        return go.Scatter(
            name="[T] Buy", x=buy.index, y=buy, visible='legendonly',
            mode='markers', marker=dict(symbol='triangle-up', color='green', size=8),
            xhoverformat="%Y/%m/%d", yhoverformat=",.2f", hovertemplate="%{x}<br>%{y}" + self.curr + "<extra>Buy</extra>"
        )

    @property
    def figure_basic(self) -> go.Figure:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_width=[0.2, 0.8], vertical_spacing=0.01)

        fig.add_trace(self.trace_upper_edge, row=1, col=1)

        trace_middle = self.trace_middle
        trace_middle.line = dict(color='rgb(197, 224, 180)')
        fig.add_trace(trace_middle, row=1, col=1)

        trace_lower = self.trace_lower_edge
        trace_lower.line = dict(color='rgb(197, 224, 180)')
        fig.add_trace(trace_lower, row=1, col=1)

        trace_price = draw_candle(data=self.ohlcv, name=self.name)
        fig.add_trace(trace_price, row=1, col=1)

        trace_volume = draw_bar(data=self.ohlcv.거래량, name="거래량")
        trace_volume.marker = dict(color=self.ohlcv.거래량.pct_change().apply(lambda x: 'blue' if x < 0 else 'red'))
        fig.add_trace(trace_volume, row=2, col=1)

        fig.update_layout(
            title=f"볼린저밴드: {self.name}", plot_bgcolor="white", height=750,
            legend=dict(tracegroupgap=5),
            xaxis=dict(
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                showline=True, linewidth=1, linecolor='grey', mirror=False
            ),
            yaxis=dict(
                title=f"{self.name}[{'-' if not self.curr else self.curr}]",
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                showline=True, linewidth=0.5, linecolor='grey', mirror=False
            ),
            xaxis2=dict(
                showticklabels=True, tickformat='%Y/%m/%d',
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                showline=True, linewidth=1, linecolor='grey', mirror=False
            ),
            yaxis2=dict(
                title=f"거래량",
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                showline=True, linewidth=0.5, linecolor='grey', mirror=False
            ),
            xaxis_rangeslider=dict(visible=False),
            xaxis_rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
        )
        return fig

    @property
    def figure_full(self) -> go.Figure:
        fig = make_subplots(
            rows=4, cols=1, shared_xaxes=True,
            row_width=[0.2, 0.2, 0.15, 0.5], vertical_spacing=0.02
        )
        fig.add_trace(self.trace_upper_edge, row=1, col=1)
        fig.add_trace(self.trace_upper_trend, row=1, col=1)
        fig.add_trace(self.trace_middle, row=1, col=1)
        fig.add_trace(self.trace_lower_trend, row=1, col=1)
        fig.add_trace(self.trace_lower_edge, row=1, col=1)

        fig.add_trace(self.trace_width, row=3, col=1)
        fig.add_trace(self.trace_pctb, row=4, col=1)
        fig.add_hrect(y0=0, y1=1, line_width=0, fillcolor='green', opacity=0.2, row=4, col=1)

        trace_price = draw_candle(data=self.ohlcv, name=self.name)
        trace_price.showlegend = False
        trace_volume = draw_bar(data=self.ohlcv.거래량, name="거래량")
        trace_volume.marker = dict(color=self.ohlcv.거래량.pct_change().apply(lambda x: 'blue' if x < 0 else 'red'))
        fig.add_trace(trace_price, row=1, col=1)
        fig.add_trace(trace_volume, row=2, col=1)
        fig.add_trace(self.trace_traditional_buy, row=1, col=1)
        fig.add_trace(self.trace_traditional_sell, row=1, col=1)

        fig.update_layout(
            title=f"볼린저밴드: {self.name}", plot_bgcolor="white", height=750,
            legend=dict(tracegroupgap=5),
            xaxis=dict(
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                showline=True, linewidth=1, linecolor='grey', mirror=False
            ),
            yaxis=dict(
                title=f"{self.name}[{self.curr}]",
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                showline=True, linewidth=0.5, linecolor='grey', mirror=False
            ),
            xaxis2=dict(
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                showline=True, linewidth=1, linecolor='grey', mirror=False
            ),
            yaxis2=dict(
                title=f"거래량",
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                showline=True, linewidth=0.5, linecolor='grey', mirror=False
            ),
            xaxis3=dict(
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                showline=True, linewidth=1, linecolor='grey', mirror=False
            ),
            yaxis3=dict(
                title=f"밴드폭[%]",
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                showline=True, linewidth=0.5, linecolor='grey', mirror=False
            ),
            xaxis4=dict(
                showticklabels=True, tickformat='%Y/%m/%d',
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                showline=True, linewidth=1, linecolor='grey', mirror=False
            ),
            yaxis4=dict(
                title=f"%B[-]",
                showgrid=True, gridwidth=0.5, gridcolor='lightgrey', autorange=True,
                zeroline=True, zerolinewidth=0.5, zerolinecolor='grey',
                showline=True, linewidth=0.5, linecolor='grey', mirror=False
            ),
            xaxis_rangeslider=dict(visible=False),
            xaxis_rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
        )
        return fig

# Alias
bollinger_band = _traces