from tdatlib import ohlcv
from tdatlib.view.stock.toolbox import *
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as of


class technical(ohlcv):

    def __init__(self, ticker:str, period:int=5):
        """
        기본형 데이터 초기화: 일봉, 가격, 거래량, 볼린저밴드
        """
        super().__init__(ticker=ticker, period=period)

        self.__candle = go.Candlestick(
            name='일봉', x=self.ohlcv.index,
            open=self.ohlcv.시가, high=self.ohlcv.고가, low=self.ohlcv.저가, close=self.ohlcv.종가,
            increasing_line=dict(color='red'), decreasing_line=dict(color='royalblue'),
            visible=True, showlegend=True,
        )
        self.__prices = [
            go.Scatter(
                name=n, x=self.ohlcv.index, y=self.ohlcv[n],
                visible='legendonly', showlegend=True,
                meta=reform(span=self.ohlcv.index),
                hovertemplate='날짜: %{meta}<br>' + n + ': %{y:,}' + f'{self.currency}<extra></extra>'
            )
            for n in ['시가', '고가', '저가', '종가']
        ]
        self.__volume = go.Bar(
            name='거래량', x=self.ohlcv.index, y=self.ohlcv.거래량,
            marker=dict(color=['blue' if d < 0 else 'red' for d in self.ohlcv.거래량.pct_change().fillna(1)]),
            visible=True, showlegend=True,
            meta=reform(span=self.ohlcv.index),
            hovertemplate='날짜:%{meta}<br>거래량:%{y:,d}<extra></extra>'
        )
        self.__band = [
            go.Scatter(
                name='볼린저밴드', x=df.index, y=df,
                mode='lines', line=dict(color='rgb(184, 247, 212)'), fill='tonexty' if n else None,
                visible=True, showlegend=False if n else True, legendgroup='볼린저밴드',
                meta=reform(span=df.index),
                hovertemplate=name + '<br>날짜: %{meta}<br>값: %{y:,d}원<extra></extra>',
            ) for n, (df, name) in enumerate([
                (self.ta.volatility_bbh, '상한'), (self.ta.volatility_bbm, '기준'), (self.ta.volatility_bbl, '하한')
            ])
        ]
        return

    def save(self, fig:go.Figure, title:str, path:str=str()):
        """
        차트 저장
        :param fig: 차트 오브젝트
        :param title: 차트 종류
        :param path:
        """
        if path:
            of.plot(fig, filename=f'{path}/{self.name}_{title}.html', auto_open=False)
        else:
            of.plot(fig, filename=f'{archive.desktop}/{self.name}_{title}.html', auto_open=False)
        return

    def get_base(self, row_width:list, vertical_spacing:float=0.02) -> go.Figure:
        """
        기본 차트형: 일봉, 주가, 볼린저밴드, 거래량
        :param row_width: [list] 행 높이(비율)
        :param vertical_spacing: [float] 행간
        """
        rows = len(row_width)
        fig = make_subplots(rows=rows, cols=1, row_width=row_width, shared_xaxes=True, vertical_spacing=vertical_spacing)
        fig.add_trace(trace=self.__candle, row=1, col=1)
        _ = [fig.add_trace(trace=trace, row=1, col=1) for trace in self.__prices]
        _ = [fig.add_trace(trace=trace, row=1, col=1) for trace in self.__band]
        fig.add_trace(trace=self.__volume, row=2, col=1)

        layout = go.Layout(
            plot_bgcolor='white',
            xaxis=setXaxis(title=str(), label=False, xranger=True), yaxis=setYaxis(title=self.currency),
            xaxis2=setXaxis(title='날짜' if rows == 2 else str(), label=True if rows == 2 else False, xranger=False),
            yaxis2=setYaxis(title='거래량'),
            xaxis_rangeslider=dict(visible=False)
        )
        fig.update_layout(layout)
        return fig

    @property
    def fig_basic(self) -> go.Figure:
        """
        직선 추세선 차트
        """
        fig = self.get_base(row_width=[0.15, 0.85], vertical_spacing=0.02)

        # for col in self.pivot.columns:
        #     color = 'red' if col == '고점' else 'royalblue'
        #     fig.add_trace(trace=traceScatter(data=self.pivot[col], unit=self.currency, color=color), row=1, col=1)
        for col in self.sma.columns:
            fig.add_trace(traceLine(data=self.sma[col], name=col, visible='legendonly'))
        for gap in ['2M', '3M', '6M', '1Y']:
            t, n = self.get_trend(gap=gap), f'{gap}평균'
            fig.add_trace(traceLine(data=t.resist, name=n, visible='legendonly', legendgroup=n, showlegend=False))
            fig.add_trace(traceLine(data=t.support, name=n, visible='legendonly', legendgroup=n))

            b, m = self.get_bound(gap=gap), f'{gap}지지/저항'
            fig.add_trace(traceLine(data=b.resist, name=m, visible='legendonly', legendgroup=m, showlegend=False))
            fig.add_trace(traceLine(data=b.support, name=m, visible='legendonly', legendgroup=m))
        fig.update_layout(title=f'{self.name}({self.ticker}) 직선 추세 차트')
        return fig

    @property
    def fig_bb(self) -> go.Figure:
        """
        볼린저 밴드: 밴드, 폭, 신호
        """
        fig = self.get_base(row_width=[0.15, 0.15, 0.1, 0.6])

        fig.add_trace(trace=traceLine(data=self.ta.volatility_bbw, name='밴드폭', unit='%'), row=3, col=1)
        fig.add_trace(trace=traceLine(data=self.ta.volatility_bbp, name='신호', unit=''), row=4, col=1)
        fig.update_layout(
            title=f'{self.name}({self.ticker}) 볼린저밴드',
            xaxis3=setXaxis(title=str(), label=False, xranger=False), yaxis3=setYaxis(title='폭[%]'),
            xaxis4=setXaxis(title='날짜', xranger=False), yaxis4=setYaxis(title='신호[-]'),
        )
        return fig

    @property
    def fig_rsi(self) -> go.Figure:
        """
        RSI 계열: Relative Strength Index
        """
        fig = self.get_base(row_width=[0.25, 0.25, 0.1, 0.4])

        fig.add_trace(trace=traceLine(data=self.ta.momentum_rsi, name='RSI', unit='%'), row=3, col=1)
        fig.add_hrect(y0=70, y1=80, line_width=0, fillcolor='red', opacity=0.2, row=3, col=1)
        fig.add_hrect(y0=20, y1=30, line_width=0, fillcolor='green', opacity=0.2, row=3, col=1)
        fig.add_trace(trace=traceLine(data=self.ta.momentum_stoch, name='S-RSI', unit='%'), row=4, col=1)
        fig.add_trace(trace=traceLine(data=self.ta.momentum_stoch_signal, name='S-RSI-Sig', unit='%'), row=4, col=1)
        fig.add_hrect(y0=80, y1=100, line_width=0, fillcolor='red', opacity=0.2, row=4, col=1)
        fig.add_hrect(y0=0, y1=20, line_width=0, fillcolor='green', opacity=0.2, row=4, col=1)
        fig.update_layout(
            title=f'{self.name}({self.ticker}) RSI',
            xaxis3=setXaxis(title=str(), label=False, xranger=False), yaxis3=setYaxis(title='RSI[%]'),
            xaxis4=setXaxis(title='날짜', xranger=False), yaxis4=setYaxis(title='S-RSI[%]'),
        )
        return fig

    @property
    def fig_macd(self) -> go.Figure:
        """
        MACD: Moving Average Convergence Divergence
        """
        fig = self.get_base(row_width=[0.3, 0.1, 0.6])

        fig.add_trace(trace=traceLine(data=self.ta.trend_macd, name='MACD', unit=''), row=3, col=1)
        fig.add_trace(trace=traceLine(data=self.ta.trend_macd_signal, name='Signal', unit=''), row=3, col=1)
        fig.add_trace(trace=traceBar(data=self.ta.trend_macd_diff, name='Histogram', color='zc'), row=3, col=1)
        fig.add_hline(y=0, line_width=0.5, line_dash="dash", line_color="black", row=3, col=1)
        fig.update_layout(
            title=f'{self.name}({self.ticker}) MACD',
            xaxis3=setXaxis(title='날짜', label=True, xranger=False), yaxis3=setYaxis(title='MACD'),
        )
        return fig

    @property
    def fig_cci(self) -> go.Figure:
        """
        CCI: Commodity Channel Index
        """
        fig = self.get_base(row_width=[0.3, 0.1, 0.6])

        fig.add_trace(trace=traceLine(data=self.ta.trend_cci, name='CCI', unit='%'), row=3, col=1)
        fig.add_hrect(y0=200, y1=400, line_width=0, fillcolor='red', opacity=0.2, row=3, col=1)
        fig.add_hrect(y0=100, y1=200, line_width=0, fillcolor='brown', opacity=0.2, row=3, col=1)
        fig.add_hrect(y0=-200, y1=-100, line_width=0, fillcolor='lightgreen', opacity=0.4, row=3, col=1)
        fig.add_hrect(y0=-400, y1=-200, line_width=0, fillcolor='green', opacity=0.2, row=3, col=1)
        fig.update_layout(
            title=f'{self.name}({self.ticker}) CCI',
            xaxis3=setXaxis(title='날짜', label=True, xranger=False), yaxis3=setYaxis(title='CCI'),
        )
        return fig

    @property
    def fig_vortex(self) -> go.Figure:
        """
        VORTEX
        """
        fig = self.get_base(row_width=[0.15, 0.35, 0.1, 0.4])

        fig.add_trace(trace=traceLine(data=self.ta.trend_vortex_ind_pos, name='TRIX(+)', color='red'), row=3, col=1)
        fig.add_trace(trace=traceLine(data=self.ta.trend_vortex_ind_neg, name='TRIX(-)', color='blue'), row=3, col=1)
        fig.add_trace(trace=traceLine(data=self.ta.trend_vortex_ind_diff, name='TRIX-Sig', color='brown'), row=4, col=1)
        fig.add_hline(y=0, line_width=0.5, line_dash="dash", line_color="black", row=4, col=1)
        fig.update_layout(
            title=f'{self.name}({self.ticker}) VORTEX',
            xaxis3=setXaxis(title=str(), label=False, xranger=False), yaxis3=setYaxis(title='VORTEX'),
            xaxis4=setXaxis(title='날짜', label=True, xranger=False), yaxis4=setYaxis(title='VORTEX-Sig'),
        )
        return fig

    @property
    def fig_stc(self) -> go.Figure:
        """
        STC: Schaff Trend Cycle
        """
        fig = self.get_base(row_width=[0.3, 0.1, 0.6])

        fig.add_trace(trace=traceLine(data=self.ta.trend_stc, name='STC', unit='%'), row=3, col=1)
        fig.update_layout(
            title=f'{self.name}({self.ticker}) STC',
            xaxis3=setXaxis(title='날짜', label=True, xranger=False), yaxis3=setYaxis(title='STC'),
        )
        return fig

    @property
    def fig_trix(self) -> go.Figure:
        """
        TRIX
        """
        fig = self.get_base(row_width=[0.3, 0.1, 0.6])

        fig.add_trace(trace=traceLine(data=self.ta.trend_trix, name='TRIX', unit='[-]'), row=3, col=1)
        fig.update_layout(
            title=f'{self.name}({self.ticker}) TRIX',
            xaxis3=setXaxis(title='날짜', label=True, xranger=False), yaxis3=setYaxis(title='TRIX'),
        )
        return fig


if __name__ == "__main__":
    from tdatlib import archive
    from pykrx import stock as krx
    import random, os, datetime

    tickers = krx.get_index_portfolio_deposit_file(ticker='1028')
    ticker = random.sample(tickers, 1)[0]
    # ticker = 'COKE'
    # ticker = '093370'

    t_analyze = technical(ticker=ticker, period=3)
    print(t_analyze.name, ticker)

    # t_analyze.fig_basic.show()
    # t_analyze.fig_bb.show()
    # t_analyze.fig_rsi.show()
    # t_analyze.fig_macd.show()
    # t_analyze.fig_cci.show()
    # t_analyze.fig_stc.show()
    # t_analyze.fig_trix.show()


    path = os.path.join(archive.desktop, f'tdat/{datetime.datetime.today().strftime("%Y-%m-%d")}')
    if not os.path.isdir(path):
        os.makedirs(path)
    # t_analyze.save(t_analyze.fig_basic, title='직선추세', path=path)
    # t_analyze.save(t_analyze.fig_bb, title='볼린저밴드', path=path)
    # t_analyze.save(t_analyze.fig_macd, title='MACD', path=path)
    # t_analyze.save(t_analyze.fig_rsi, title='RSI', path=path)
    # t_analyze.save(t_analyze.fig_cci, title='CCI', path=path)
    # t_analyze.save(t_analyze.fig_stc, title='STC', path=path)
    # t_analyze.save(t_analyze.fig_trix, title='TRIX', path=path)
    # t_analyze.save(t_analyze.fig_vortex, title='VORTEX', path=path)
