from tdatlib.viewer.stock.ohlcv.core import chart
from tdatlib.viewer.tools import save, sketch
from plotly.subplots import make_subplots
from tqdm import tqdm
import plotly.graph_objects as go


class ohlcv(chart):

    _skh = sketch()

    def saveall(self, path:str=str()):
        proc = tqdm([
            (self.fig_basis, 'Basic'),
            (self.fig_bollinger_band, 'Bollinger Band'),
            (self.fig_macd, 'MACD'),
            (self.fig_rsi, 'RSI'),
            (self.fig_mfi, 'MFI'),
            (self.fig_cci, 'CCI'),
            (self.fig_vortex, 'Vortex'),
            (self.fig_trix, 'Trix')
        ])
        for n, (fig, name) in enumerate(proc):
            proc.set_description(desc=f'{self.tag}: {name}')
            save(fig=fig, filename=f'{self.tag}-T{str(n + 1).zfill(2)}_{name}', path=path)
        return

    @property
    def tag(self) -> str:
        return f'{self.src.label}' if self.src.currency == 'USD' else f'{self.src.label}({self.src.ticker})'

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
        fig.add_trace(self.candle, row=1, col=1)

        # Price
        for ch in self.price.values():
            fig.add_trace(ch, row=1, col=1)

        # MA
        for ch in self.ma.values():
            fig.add_trace(ch, row=1, col=1)

        # NC
        for ch in self.nc.values():
            fig.add_trace(ch, row=1, col=1)

        # Trend
        for ch in self.trend.values():
            fig.add_trace(ch, row=1, col=1)

        # Support / Resist
        for ch in self.bound.values():
            resist, support = ch
            fig.add_trace(resist, row=1, col=1)
            fig.add_trace(support, row=1, col=1)

        # Volume
        fig.add_trace(self.volume, row=2, col=1)

        fig.update_layout(
            title=f'{self.tag} 기본 차트',
            plot_bgcolor='white',
            legend=dict(
                # groupclick="toggleitem",
                tracegroupgap=5
            ),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self.src.currency),
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
        fig.add_trace(self.candle, row=1, col=1)

        # Price
        for trace in self.price.values():
            fig.add_trace(trace, row=1, col=1)

        # Bollinger-Band
        for trace in self.bb:
            fig.add_trace(trace=trace, row=1, col=1)

        # Inner Band
        for trace in self.bb_inner:
            fig.add_trace(trace=trace, row=1, col=1)

        # Volume
        fig.add_trace(self.volume, row=2, col=1)

        # Width
        fig.add_trace(self.bb_width, row=3, col=1)

        # Tag
        fig.add_trace(self.bb_tag, row=4, col=1)
        mx = getattr(self.src.ohlcv_bband, 'signal').max()
        mn = getattr(self.src.ohlcv_bband, 'signal').min()
        fig.add_hrect(y0=1, y1=mx, line_width=0, fillcolor='red', opacity=0.2, row=4, col=1)
        fig.add_hrect(y0=mn, y1=0, line_width=0, fillcolor='green', opacity=0.2, row=4, col=1)

        # Inner Band Contain
        fig.add_trace(self.bb_contain, row=5, col=1)

        # Squeeze Break - Point
        fig.add_trace(self.bb_breakout, row=1, col=1)

        fig.update_layout(
            title=f'{self.tag} Bollinger Band',
            plot_bgcolor='white',
            # legend=dict(groupclick="toggleitem"),
            legend=dict(tracegroupgap=5),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self.src.currency),
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
        fig = make_subplots(
            rows=3,
            cols=1,
            row_width=[0.3, 0.1, 0.6],
            shared_xaxes=True,
            vertical_spacing=0.02
        )

        # Candle Stick
        fig.add_trace(self.candle, row=1, col=1)

        # Price
        for trace in self.price.values():
            fig.add_trace(trace, row=1, col=1)

        # MA
        for ch in self.ma.values():
            fig.add_trace(ch, row=1, col=1)

        # Volume
        fig.add_trace(self.volume, row=2, col=1)

        # MACD
        fig.add_trace(self.macd, row=3, col=1)
        fig.add_trace(self.macd_sig, row=3, col=1)
        fig.add_trace(self.macd_diff, row=3, col=1)
        fig.add_hline(y=0, row=3, col=1, line_width=0.5, line_dash="dot", line_color="black")

        fig.update_layout(
            title=f'{self.tag} MACD',
            plot_bgcolor='white',
            legend=dict(
                groupclick="toggleitem",
                tracegroupgap=5
            ),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self.src.currency),
            xaxis2=self._skh.x_axis(),
            yaxis2=self._skh.y_axis(title='거래량'),
            xaxis3=self._skh.x_axis(title='날짜', showticklabels=True),
            yaxis3=self._skh.y_axis(title='MACD'),
            xaxis_rangeslider=dict(visible=False)
        )
        return fig

    @property
    def fig_rsi(self) -> go.Figure:
        fig = make_subplots(
            rows=4,
            cols=1,
            row_width=[0.25, 0.25, 0.1, 0.4],
            shared_xaxes=True,
            vertical_spacing=0.02
        )

        # Candle Stick
        fig.add_trace(self.candle, row=1, col=1)

        # Price
        for trace in self.price.values():
            fig.add_trace(trace, row=1, col=1)

        # MA
        for ch in self.ma.values():
            fig.add_trace(ch, row=1, col=1)

        # Volume
        fig.add_trace(self.volume, row=2, col=1)

        # RSI
        fig.add_trace(self.rsi, row=3, col=1)
        fig.add_hrect(y0=70, y1=80, line_width=0, fillcolor='red', opacity=0.2, row=3, col=1)
        fig.add_hrect(y0=20, y1=30, line_width=0, fillcolor='green', opacity=0.2, row=3, col=1)

        # Stochastic RSI
        fig.add_trace(self.stoch_rsi, row=4, col=1)
        fig.add_trace(self.stoch_rsi_sig, row=4, col=1)
        fig.add_hrect(y0=80, y1=100, line_width=0, fillcolor='red', opacity=0.2, row=4, col=1)
        fig.add_hrect(y0=0, y1=20, line_width=0, fillcolor='green', opacity=0.2, row=4, col=1)

        fig.update_layout(
            title=f'{self.tag} RSI',
            plot_bgcolor='white',
            legend=dict(
                groupclick="toggleitem",
                tracegroupgap=5
            ),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self.src.currency),
            xaxis2=self._skh.x_axis(),
            yaxis2=self._skh.y_axis(title='거래량'),
            xaxis3=self._skh.x_axis(),
            yaxis3=self._skh.y_axis(title='RSI'),
            xaxis4=self._skh.x_axis(title='날짜', showticklabels=True),
            yaxis4=self._skh.y_axis(title='Stoch-RSI'),
            xaxis_rangeslider=dict(visible=False)
        )
        return fig

    @property
    def fig_mfi(self) -> go.Figure:
        fig = make_subplots(
            rows=3,
            cols=1,
            row_width=[0.3, 0.2, 0.5],
            shared_xaxes=True,
            vertical_spacing=0.02
        )

        # Candle Stick
        fig.add_trace(self.candle, row=1, col=1)

        # Price
        for trace in self.price.values():
            fig.add_trace(trace, row=1, col=1)

        # MA
        for ch in self.ma.values():
            fig.add_trace(ch, row=1, col=1)

        # Volume
        fig.add_trace(self.volume, row=2, col=1)

        # MFI
        fig.add_trace(self.mfi, row=3, col=1)
        fig.add_hrect(y0=80, y1=100, line_width=0, fillcolor='red', opacity=0.2, row=3, col=1)
        fig.add_hline(y=90, line_width=0.5, line_dash="dash", line_color="black", row=3, col=1)
        fig.add_hrect(y0=0, y1=20, line_width=0, fillcolor='lightgreen', opacity=0.4, row=3, col=1)
        fig.add_hline(y=10, line_width=0.5, line_dash="dash", line_color="black", row=3, col=1)

        fig.update_layout(
            title=f'{self.tag} MFI',
            plot_bgcolor='white',
            legend=dict(
                groupclick="toggleitem",
                tracegroupgap=5
            ),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self.src.currency),
            xaxis2=self._skh.x_axis(),
            yaxis2=self._skh.y_axis(title='거래량'),
            xaxis3=self._skh.x_axis(title='날짜', showticklabels=True),
            yaxis3=self._skh.y_axis(title='MFI'),
            xaxis_rangeslider=dict(visible=False)
        )
        return fig

    @property
    def fig_cci(self) -> go.Figure:
        fig = make_subplots(
            rows=3,
            cols=1,
            row_width=[0.3, 0.2, 0.5],
            shared_xaxes=True,
            vertical_spacing=0.02
        )

        # Candle Stick
        fig.add_trace(self.candle, row=1, col=1)

        # Price
        for trace in self.price.values():
            fig.add_trace(trace, row=1, col=1)

        # MA
        for ch in self.ma.values():
            fig.add_trace(ch, row=1, col=1)

        # Volume
        fig.add_trace(self.volume, row=2, col=1)

        # CCI
        fig.add_trace(self.cci, row=3, col=1)
        fig.add_hrect(y0=200, y1=400, line_width=0, fillcolor='red', opacity=0.2, row=3, col=1)
        fig.add_hrect(y0=100, y1=200, line_width=0, fillcolor='brown', opacity=0.2, row=3, col=1)
        fig.add_hrect(y0=-200, y1=-100, line_width=0, fillcolor='lightgreen', opacity=0.4, row=3, col=1)
        fig.add_hrect(y0=-400, y1=-200, line_width=0, fillcolor='green', opacity=0.2, row=3, col=1)

        fig.update_layout(
            title=f'{self.tag} CCI',
            plot_bgcolor='white',
            legend=dict(
                groupclick="toggleitem",
                tracegroupgap=5
            ),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self.src.currency),
            xaxis2=self._skh.x_axis(),
            yaxis2=self._skh.y_axis(title='거래량'),
            xaxis3=self._skh.x_axis(title='날짜', showticklabels=True),
            yaxis3=self._skh.y_axis(title='CCI'),
            xaxis_rangeslider=dict(visible=False)
        )
        return fig

    @property
    def fig_vortex(self) -> go.Figure:
        fig = make_subplots(
            rows=3,
            cols=1,
            row_width=[0.3, 0.2, 0.5],
            shared_xaxes=True,
            vertical_spacing=0.02
        )

        # Candle Stick
        fig.add_trace(self.candle, row=1, col=1)

        # Price
        for trace in self.price.values():
            fig.add_trace(trace, row=1, col=1)

        # MA
        for ch in self.ma.values():
            fig.add_trace(ch, row=1, col=1)

        # Volume
        fig.add_trace(self.volume, row=2, col=1)

        # Vortex
        fig.add_trace(self.vortex, row=3, col=1)
        fig.add_hline(y=0, line_width=0.5, line_color='black', line_dash='dot', row=3, col=1)

        fig.update_layout(
            title=f'{self.tag} Vortex',
            plot_bgcolor='white',
            legend=dict(
                groupclick="toggleitem",
                tracegroupgap=5
            ),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self.src.currency),
            xaxis2=self._skh.x_axis(),
            yaxis2=self._skh.y_axis(title='거래량'),
            xaxis3=self._skh.x_axis(title='날짜', showticklabels=True),
            yaxis3=self._skh.y_axis(title='Vortex'),
            xaxis_rangeslider=dict(visible=False)
        )
        return fig

    @property
    def fig_trix(self) -> go.Figure:
        fig = make_subplots(
            rows=3,
            cols=1,
            row_width=[0.3, 0.2, 0.5],
            shared_xaxes=True,
            vertical_spacing=0.02
        )

        # Candle Stick
        fig.add_trace(self.candle, row=1, col=1)

        # Price
        for trace in self.price.values():
            fig.add_trace(trace, row=1, col=1)

        # MA
        for ch in self.ma.values():
            fig.add_trace(ch, row=1, col=1)

        # Volume
        fig.add_trace(self.volume, row=2, col=1)

        # Trix
        fig.add_trace(self.trix, row=3, col=1)
        # fig.add_hline(y=0, line_width=0.5, line_color='black', line_dash='dot', row=3, col=1)

        fig.update_layout(
            title=f'{self.tag} Trix',
            plot_bgcolor='white',
            legend=dict(
                groupclick="toggleitem",
                tracegroupgap=5
            ),
            xaxis=self._skh.x_axis(rangeselector=True),
            yaxis=self._skh.y_axis(title=self.src.currency),
            xaxis2=self._skh.x_axis(),
            yaxis2=self._skh.y_axis(title='거래량'),
            xaxis3=self._skh.x_axis(title='날짜', showticklabels=True),
            yaxis3=self._skh.y_axis(title='Trix'),
            xaxis_rangeslider=dict(visible=False)
        )
        return fig


if __name__ == "__main__":
    from tdatlib.dataset.stock.ohlcv import technical

    # path = r'\\kefico\keti\ENT\Softroom\Temp\J.H.Lee'
    path = str()

    # data = technical(ticker='185750', period=3)
    # data = technical(ticker='TSLA', period=3)
    data = technical(ticker='253450', period=3)

    viewer = ohlcv(src = data)

    viewer.saveall()
    # save(fig=viewer.fig_basis, filename=f'{viewer.tag}-01_Basic', path=path)
    # save(fig=viewer.fig_bollinger_band, filename=f'{viewer.tag}-02_Bollinger', path=path)
    # save(fig=viewer.fig_macd, filename=f'{viewer.tag}-03_MACD', path=path)
    # save(fig=viewer.fig_rsi, filename=f'{viewer.tag}-04_RSI', path=path)
    # save(fig=viewer.fig_mfi, filename=f'{viewer.tag}-05_MFI', path=path)
    # save(fig=viewer.fig_cci, filename=f'{viewer.tag}-06_CCI', path=path)
    # save(fig=viewer.fig_vortex, filename=f'{viewer.tag}-07_VORTEX', path=path)
    # save(fig=viewer.fig_trix, filename=f'{viewer.tag}-08_TRIX', path=path)