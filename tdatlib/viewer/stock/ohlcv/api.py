from tdatlib.dataset.stock.ohlcv import technical as src
from tdatlib.viewer.stock.ohlcv.core import (
    sketch,
    chart
)
from tdatlib.viewer.tools import CD_RANGER, save
from tdatlib.dataset import tools
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


class technical(object):

    _skh = sketch()
    def __init__(self, ticker:str, name:str=str(), period:int=5, endate:str=str()):
        self.ticker = ticker

        self._src = src(ticker=ticker, period=period, endate=endate)
        self._cht = chart(obj=self._src)
        if name:
            self._src.label = name
        self.name = self._src.label
        return

    @property
    def fig_basis(self) -> go.Figure:
        fig = make_subplots(
            rows=2,
            cols=1,
            row_width=[0.2, 0.8],
            shared_xaxes=True,
            vertical_spacing=0.02
        )

        # Candle Stick
        fig.add_trace(self._cht.candle, row=1, col=1)

        # Price
        for ch in self._cht.price.values():
            fig.add_trace(ch, row=1, col=1)

        # MA
        for ch in self._cht.ma.values():
            fig.add_trace(ch, row=1, col=1)

        # NC
        for ch in self._cht.nc.values():
            fig.add_trace(ch, row=1, col=1)

        # Trend
        for ch in self._cht.trend.values():
            fig.add_trace(ch, row=1, col=1)

        # Support / Resist
        for ch in self._cht.bound.values():
            resist, support = ch
            fig.add_trace(resist, row=1, col=1)
            fig.add_trace(support, row=1, col=1)

        # Volume
        fig.add_trace(self._cht.volume, row=2, col=1)

        fig.update_layout(
            title=f'{self._src.label}({self.ticker}) 기본 차트',
            plot_bgcolor='white',
            legend=dict(
                groupclick="toggleitem",
                tracegroupgap=5
            ),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self._src.currency),
            xaxis2=self._skh.x_axis(title='날짜', showticklabels=True),
            yaxis2=self._skh.y_axis(title='거래량'),
            xaxis_rangeslider=dict(visible=False)
        )
        return fig

    @property
    def fig_bollinger_band(self) -> go.Figure:
        fig = make_subplots(
            rows=5,
            cols=1,
            row_width=[0.15, 0.15, 0.15, 0.1, 0.45],
            shared_xaxes=True,
            vertical_spacing=0.02
        )

        # Candle Stick
        fig.add_trace(self._cht.candle, row=1, col=1)

        # Price
        for trace in self._cht.price.values():
            fig.add_trace(trace, row=1, col=1)

        # Bollinger-Band
        for trace in self._cht.bb:
            fig.add_trace(trace=trace, row=1, col=1)

        # Inner Band
        for trace in self._cht.bb_inner:
            fig.add_trace(trace=trace, row=1, col=1)

        # Volume
        fig.add_trace(self._cht.volume, row=2, col=1)

        # Width
        fig.add_trace(self._cht.bb_width, row=3, col=1)

        # Tag
        fig.add_trace(self._cht.bb_tag, row=4, col=1)
        mx = getattr(self._src.ohlcv_bband, 'signal').max()
        mn = getattr(self._src.ohlcv_bband, 'signal').min()
        fig.add_hrect(y0=1, y1=mx, line_width=0, fillcolor='red', opacity=0.2, row=4, col=1)
        fig.add_hrect(y0=mn, y1=0, line_width=0, fillcolor='green', opacity=0.2, row=4, col=1)

        # Inner Band Contain
        fig.add_trace(self._cht.bb_contain, row=5, col=1)

        # Squeeze Break - Point
        fig.add_trace(self._cht.bb_breakout, row=1, col=1)

        """
        Squeeze & Break 지점
        """
        fig.update_layout(
            title=f'{self._src.label}({self.ticker}) 기본 차트',
            plot_bgcolor='white',
            # legend=dict(groupclick="toggleitem"),
            legend=dict(tracegroupgap=5),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self._src.currency),
            xaxis2=self._skh.x_axis(),
            yaxis2=self._skh.y_axis(title='거래량'),
            xaxis3=self._skh.x_axis(),
            yaxis3=self._skh.y_axis(title='폭(변동성)[%]'),
            xaxis4=self._skh.x_axis(),
            yaxis4=self._skh.y_axis(title='신호[-]'),
            xaxis5=self._skh.x_axis(title='날짜', showticklabels=True),
            yaxis5=self._skh.y_axis(title='추세[%]'),
            xaxis_rangeslider=dict(visible=False)
        )
        return fig

    @property
    def fig_macd(self) -> go.Figure:
        fig = self.__frm__(row_width=[0.3, 0.1, 0.6])

        return fig


if __name__ == "__main__":

    path = r'\\kefico\keti\ENT\Softroom\Temp\J.H.Lee'
    # path = str()

    viewer = technical(ticker='185750', period=3)
    # viewer.fig_basis.show()
    # save(fig=viewer.fig_basis, filename=f'{viewer.ticker}({viewer.name})-01_기본_차트', path=path)
    save(fig=viewer.fig_bollinger_band, filename=f'{viewer.ticker}({viewer.name})-02_볼린저_밴드', path=path)


    # for ticker in ["011370", "104480", "048550", "130660", "052690", "045660", "091590", "344820", "014970", "063440", "069540"]:
    #     viewer = technical(ticker=ticker, period=2)
    #     save(fig=viewer.fig_basis, filename=f'{viewer.ticker}({viewer.name})-01_기본_차트', path=path)
    #     save(fig=viewer.fig_bollinger_band, filename=f'{viewer.ticker}({viewer.name})-02_볼린저_밴드', path=path)