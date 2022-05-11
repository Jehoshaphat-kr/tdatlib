from tdatlib.dataset.stock.ohlcv import technical as data
from tdatlib.viewer.tools import CD_RANGER, save
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


class technical(object):

    def __init__(self, ticker:str, name:str=str(), period:int=5, endate:str=str()):
        self.__tech = data(ticker=ticker, period=period, endate=endate)
        self.__name = name
        self.hx = '%{x}'
        self.hyf = '%{y:,.2f}'
        self.hyd = '%{y:,d}'
        self.hp = self.hyd if self.__tech.currency == '원' else self.hyf
        return

    def default(self, row_width: list = None, vertical_spacing: float = 0.02):
        row_width = [0.2, 0.8] if not row_width else row_width
        rows = len(row_width)
        fig = make_subplots(
            rows=rows,
            cols=1,
            row_width=row_width,
            shared_xaxes=True,
            vertical_spacing=vertical_spacing
        )
        
        if not hasattr(self, '__candle'):
            self.__setattr__(
                '__candle',
                go.Candlestick(
                    name='봉차트',
                    x=self.__tech.ohlcv.index,
                    open=self.__tech.ohlcv.시가,
                    high=self.__tech.ohlcv.고가,
                    low=self.__tech.ohlcv.저가,
                    close=self.__tech.ohlcv.종가,
                    visible=True, 
                    showlegend=True, 
                    legendgrouptitle=dict(text='캔들차트'),                    
                    increasing_line=dict(color='red'), 
                    decreasing_line=dict(color='royalblue'),
                    xhoverformat='%Y/%-m/%-d'
                )
            )
        fig.add_trace(trace=self.__getattribute__('__candle'), row=1, col=1)

        for n, col in enumerate(['시가', '고가', '저가', '종가']):
            if not hasattr(self, f'__{col}'):
                self.__setattr__(
                    f'__{col}',
                    go.Scatter(
                        name=col,
                        x=self.__tech.ohlcv.index,
                        y=self.__tech.ohlcv[col],
                        visible='legendonly',
                        showlegend=True,
                        legendgrouptitle=dict(text='주가 차트') if not n else None,
                        hovertemplate=f'날짜: {self.hx}<br>{col}: {self.hp}{self.__tech.currency}<extra></extra>'
                    )
                )
            fig.add_trace(trace=self.__getattribute__(f'__{col}'), row=1, col=1)

        if not hasattr(self, f'__volume'):
            self.__setattr__(
                f'__volume',
                go.Bar(
                    name='거래량',
                    x=self.__tech.ohlcv.index,
                    y=self.__tech.ohlcv.거래량,
                    visible=True,
                    showlegend=False,
                    marker=dict(color=['blue' if d < 0 else 'red' for d in self.__tech.ohlcv.거래량.pct_change().fillna(1)]),
                    hovertemplate=f'날짜: {self.hx}<br>거래량: {self.hyd}<extra></extra>'
                )
            )
        fig.add_trace(trace=self.__getattribute__('__volume'), row=2, col=1)

        title, label = '날짜' if rows == 2 else '', True if rows == 2 else False
        fig.update_layout(go.Layout(
            plot_bgcolor='white',
            xaxis=dict(
                title='',
                showticklabels=False,
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=False,
                rangeselector=CD_RANGER
            ),
            yaxis=dict(
                title=self.__tech.currency,
                showticklabels=True,
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=0.5,
                linecolor='grey',
                mirror=False
            ),
            xaxis2=dict(
                title=title,
                showticklabels=label,
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=False
            ),
            yaxis2=dict(
                title='거래량',
                showticklabels=True,
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=0.5,
                linecolor='grey',
                mirror=False
            ),
            xaxis_rangeslider=dict(visible=False)
        ))
        return fig


if __name__ == "__main__":
    viewer = technical(ticker='000990')
    save(fig=viewer.default(), filename='test')