from tdatlib.dataset.stock.ohlcv import technical as _data
from tdatlib.viewer.stock.ohlcv.core import (
    sketch,
    _price,
    _bollinger
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
        self._obj   = _data(ticker=ticker, period=period, endate=endate)
        self._price = _price(obj=self._obj)
        self._bollinger = _bollinger(obj=self._obj)
        if name:
            self._obj.label = name
        self.name = self._obj.label
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
        fig.add_trace(self._obj.obj_candle(), row=1, col=1)

        # Price
        for col in ['시가', '고가', '저가', '종가']:
            fig.add_trace(self._obj.obj_price(col=col), row=1, col=1)

        # MA
        for col in self._obj.ohlcv_sma.columns:
            fig.add_trace(self._obj.obj_ma(col=col), row=1, col=1)

        # NC
        for col in self._obj.ohlcv_iir.columns:
            fig.add_trace(self._obj.obj_nc(col=col), row=1, col=1)

        # Trend
        for col in self._obj.ohlcv_trend.columns:
            fig.add_trace(self._obj.obj_trend(col=col), row=1, col=1)

        # Support / Resist
        for col in ['2M', '3M', '6M', '1Y']:
            resist, support = self._obj.obj_bound(col=col)
            fig.add_trace(resist, row=1, col=1)
            fig.add_trace(support, row=1, col=1)

        # Volume
        fig.add_trace(self._obj.obj_volume(), row=2, col=1)

        fig.update_layout(
            title=f'{self._obj.label}({self.ticker}) 기본 차트',
            plot_bgcolor='white',
            # legend=dict(groupclick="toggleitem"),
            legend=dict(tracegroupgap=5),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self._obj.currency),
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

        # Bollinger-Band
        for trace in self._obj.obj_bband():
            fig.add_trace(trace=trace, row=1, col=1)

        # Inner Band
        for trace in self._obj.obj_bband_inner():
            fig.add_trace(trace=trace, row=1, col=1)

        # Candle Stick
        fig.add_trace(self._obj.obj_candle(), row=1, col=1)

        # Price
        for col in ['시가', '고가', '저가', '종가']:
            fig.add_trace(self._obj.obj_price(col=col), row=1, col=1)

        # Volume
        fig.add_trace(self._obj.obj_volume(), row=2, col=1)

        # Width
        fig.add_trace(self._obj.obj_bband_width(), row=3, col=1)

        # Tag
        fig.add_trace(self._obj.obj_bband_tag(), row=4, col=1)
        mx = getattr(self._obj.ohlcv_bband, 'signal').max()
        mn = getattr(self._obj.ohlcv_bband, 'signal').min()
        fig.add_hrect(y0=1, y1=mx, line_width=0, fillcolor='red', opacity=0.2, row=4, col=1)
        fig.add_hrect(y0=mn, y1=0, line_width=0, fillcolor='green', opacity=0.2, row=4, col=1)

        # Inner Band Contain
        fig.add_trace(self._obj.obj_bband_contain(), row=5, col=1)

        # Squeeze Break - Point

        # if not hasattr(self, f'__bbsignal'):
        #     temp = self._obj.ohlcv_bband.est_band().copy()
        #     self.__setattr__(
        #         f'__bbsignal',
        #         # go.Scatter(
        #         #     name='신호',
        #         #     x=getattr(self._obj.ohlcv_bband, 'signal').index,
        #         #     y=getattr(self._obj.ohlcv_bband, 'signal'),
        #         #     visible=True,
        #         #     showlegend=True,
        #         #     xhoverformat='%Y/%m/%d',
        #         #     yhoverformat='.2f',
        #         #     hovertemplate='%{x}<br>신호: %{y}<extra></extra>'
        #         # )
        #         go.Scatter(
        #             name='Band-Embracing',
        #             x=temp.index,
        #             y=temp,
        #             visible=True,
        #             showlegend=True,
        #             xhoverformat='%Y/%m/%d',
        #             yhoverformat='.2f',
        #             hovertemplate='%{x}<br>신호: %{y}<extra></extra>'
        #         )
        #     )
        # fig.add_trace(trace=self.__getattribute__(f'__bbsignal'), row=4, col=1)



        """
        Squeeze & Break 지점
        """
        # breakout = getattr(self._obj.ohlcv_bband, 'hist_breakout')
        # hist_breakout = go.Scatter(
        #     name='Break-Out 지점',
        #     x=breakout.index,
        #     y=self._obj.ohlcv[self._obj.ohlcv.index.isin(breakout.index)].종가,
        #     mode='markers',
        #     marker=dict(symbol='triangle-up', color='red', size=8),
        #     visible='legendonly',
        #     showlegend=True,
        #     legendgrouptitle=dict(text='백테스트 지점'),
        #     hoverinfo='skip'
        # )
        # fig.add_trace(trace=hist_breakout, row=1, col=1)
        # pt = self.__getattribute__(f'__bbpoint').rise.dropna()
        # rise_sig = go.Scatter(
        #     name='저점-상승',
        #     x=pt.index,
        #     y=pt,
        #     mode='markers',
        #     marker=dict(symbol='triangle-up', color='lightgreen'),
        #     visible='legendonly',
        #     showlegend=True,
        #     legendgroup='매수지점',
        #     hoverinfo='skip'
        # )
        # fig.add_trace(trace=rise_sig, row=4, col=1)
        #
        # price = self._obj.ohlcv[self._obj.ohlcv.index.isin(pt.index)]
        # rise_price = go.Scatter(
        #     name='저점-상승',
        #     x=price.index,
        #     y=price.종가,
        #     mode='markers',
        #     marker=dict(symbol='triangle-up', color='lightgreen'),
        #     visible='legendonly',
        #     showlegend=False,
        #     legendgroup='매수지점',
        #     xhoverformat='%Y/%m/%d',
        #     yhoverformat=',' if self._obj.currency == '원' else ',.2f',
        #     hovertemplate='%{x}<br>매수가: %{y}<extra></extra>'
        # )
        # fig.add_trace(trace=rise_price, row=1, col=1)


        fig.update_layout(
            title=f'{self._obj.label}({self.ticker}) 기본 차트',
            plot_bgcolor='white',
            # legend=dict(groupclick="toggleitem"),
            legend=dict(tracegroupgap=5),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self._obj.currency),
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