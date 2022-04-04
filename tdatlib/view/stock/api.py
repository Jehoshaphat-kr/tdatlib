from tdatlib.view.stock.raw import *
from tdatlib import stock, archive
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as of


class analyze(stock):
    __init_done, __candle, __volume, __prices, __band = False, None, None, None, None

    def __init(self):
        """
        기본형 데이터 초기화: 일봉, 가격, 거래량, 볼린저밴드
        """
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
        self.__init_done = True
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
        if not self.__init_done:
            self.__init()

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
    def fig_pv(self) -> go.Figure:
        """
        가격, 거래량 차트
        """
        fig = self.get_base(row_width=[0.15, 0.85], vertical_spacing=0.02)
        fig.update_layout(title=f'{self.name}({self.ticker}) 가격/거래량')
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
            t, n = self.avg_trend(gap=gap), f'{gap}평균'
            fig.add_trace(traceLine(data=t.resist, name=n, visible='legendonly', legendgroup=n, showlegend=False))
            fig.add_trace(traceLine(data=t.support, name=n, visible='legendonly', legendgroup=n))

            b, m = self.bound(gap=gap), f'{gap}지지/저항'
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

    # -------------------------------------------------------------------------------------------------------------- #

    @property
    def fig_overview(self) -> go.Figure:
        """
        제품 구성, 자산 및 부채, 연간 실적, 분기 실적
        """
        fig = make_subplots(
            rows=2, cols=2, vertical_spacing=0.12, horizontal_spacing=0.1,
            subplot_titles=("제품 구성", "멀티 팩터", "자산", "연간 실적"),
            specs=[[{"type": "pie"}, {"type": "polar"}], [{"type": "bar"}, {"type": "bar"}]]
        )

        product, a_stat, q_stat = self.product.copy(), self.annual_statement.copy(), self.quarter_statement.copy()
        fig.add_trace(go.Pie(
            name='Product', labels=product.index, values=product,
            textinfo='label+percent', insidetextorientation='radial',
            visible=True, showlegend=False,
            hoverinfo='label+percent'
        ), row=1, col=1)

        multi_factor = self.multi_factor.copy()
        for n, col in enumerate(multi_factor.columns):
            fig.add_trace(go.Scatterpolar(
                name=col, r=multi_factor[col].astype(float), theta=multi_factor.index,
                fill='toself', visible=True, showlegend=True,
                hovertemplate=col + '<br>팩터: %{theta}<br>값: %{r}<extra></extra>'
            ), row=1, col=2)

        asset = a_stat[['자산총계', '부채총계', '자본총계']].fillna(0).astype(int).copy()
        c2t = lambda x: str(x) if x < 10000 else f'{str(x)[:-4]}조 {str(x)[-4:]}억원'
        fig.add_trace(go.Bar(
            name='자산', x=asset.index, y=asset.자산총계, marker=dict(color='green'), opacity=0.9,
            text=asset.자산총계.apply(c2t), meta=asset.부채총계.apply(c2t), customdata=asset.자본총계.apply(c2t),
            visible=True, showlegend=False, offsetgroup=0, texttemplate='',
            hovertemplate='자산: %{text}<br>부채: %{meta}<br>자본: %{customdata}<extra></extra>'
        ), row=2, col=1)
        fig.add_trace(go.Bar(
            name='부채', x=asset.index, y=asset.부채총계, marker=dict(color='red'), opacity=0.8,
            visible=True, showlegend=False, offsetgroup=0, hoverinfo='skip'
        ), row=2, col=1)

        key = [_ for _ in ['매출액', '순영업수익', '이자수익', '보험료수익'] if _ in a_stat.columns][0]
        require = a_stat[[key, '영업이익', '당기순이익']]
        for n, col in enumerate(require.columns):
            y = require[col].fillna(0).astype(int)
            fig.add_trace(go.Bar(
                name=f'연간{col}', x=require.index, y=y,
                marker=dict(color=colors[n]), opacity=0.9, legendgroup=col, meta=y.apply(c2t),
                hovertemplate=col + ': %{meta}<extra></extra>',
            ), row=2, col=2)

        fig.update_layout(dict(
            title=f'{self.name}[{self.ticker}] : 제품, 자산 및 실적',
            plot_bgcolor='white',
            margin=dict(l=0)
        ))
        fig.update_yaxes(title_text="억원", gridcolor='lightgrey', row=2, col=1)
        fig.update_yaxes(title_text="억원", gridcolor='lightgrey', row=2, col=2)
        for n, annotation in enumerate(fig['layout']['annotations']):
                annotation['x'] = 0 + 0.55 * (n % 2)
                annotation['xanchor']= 'center'
                annotation['xref'] = 'paper'
        return fig

    @property
    def fig_relative(self) -> go.Figure:
        """
        상대 지표: 시장 상대지표 및 PER, EV/EBITA, ROE 상대지표
        """
        fig = make_subplots(
            rows=2, cols=2, vertical_spacing=0.12, horizontal_spacing=0.1,
            subplot_titles=("상대 수익률", "PER", "EV/EBITA", "ROE"),
            specs=[[{"type": "xy"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]]
        )

        benchmark = self.benchmark_relative.copy()
        for col in ['3M', '1Y']:
            df = benchmark[col].dropna()
            for n, c in enumerate(df.columns):
                fig.add_trace(go.Scatter(
                    name=f'{col}수익률비교', x=df.index, y=df[c].astype(float),
                    visible=True if col == '3M' else 'legendonly', showlegend=True if not n else False,
                    legendgroup=f'{col}수익률비교', meta=reform(span=df.index),
                    hovertemplate='날짜: %{meta}<br>' + f'{c}: ' + '%{y:.2f}%<extra></extra>'
                ), row=1, col=1)

        mul_rel = self.multiple_relative.copy()
        for m, col in enumerate(['PER', 'EV/EBITA', 'ROE']):
            df = mul_rel[col]
            for n, c in enumerate(df.columns):
                fig.add_trace(go.Bar(
                    name=f'{col}:{c}', x=df[c].index, y=df[c], marker=dict(color=colors[n]),
                    hovertemplate='분기: %{x}<br>' + c + ': %{y:.2f}<extra></extra>'
                ), row=1 if not m else 2, col=2 if m == 0 or m == 2 else 1)

        fig.update_layout(dict(
            title=f'<b>{self.name}[{self.ticker}]</b> : 시장 상대 지표',
            plot_bgcolor='white',
        ))
        fig.update_yaxes(title_text="수익률[%]", gridcolor='lightgrey', row=1, col=1)
        fig.update_yaxes(title_text="PER[-]", gridcolor='lightgrey', row=1, col=2)
        fig.update_yaxes(title_text="EV/EBITA[-]", gridcolor='lightgrey', row=2, col=1)
        fig.update_yaxes(title_text="ROE[%]", gridcolor='lightgrey', row=2, col=2)
        fig.update_xaxes(gridcolor='lightgrey')
        return fig

    @property
    def fig_supply(self) -> go.Figure:
        """
        수급 현황: 컨센서스, 외국인 보유율, 대차잔고, 공매도
        """
        fig = make_subplots(
            rows=2, cols=2, vertical_spacing=0.11, horizontal_spacing=0.1,
            subplot_titles=("컨센서스", "외국인 보유비중", "차입공매도 비중", "대차잔고 비중"),
            specs=[[{"type": "xy"}, {"type": "xy", "secondary_y": True}],
                   [{"type": "xy", "secondary_y": True}, {"type": "xy", 'secondary_y': True}]]
        )

        consen = self.consensus[['목표주가', '종가']].astype(int).copy()
        fig.add_trace(trace=traceLine(data=consen.목표주가, name='컨센서스: 목표가', unit='원', dtype='int'), row=1, col=1)
        fig.add_trace(trace=traceLine(data=consen.종가, name='컨센서스: 종가', unit='원', dtype='int'), row=1, col=1)

        foreign = self.foreigner.copy()
        for m, col in enumerate(['3M', '1Y', '3Y']):
            df = foreign[col].dropna()
            for n, c in enumerate(df.columns):
                data = df[c].astype(float) if n else df[c].astype(int)
                name, unit, visible = f'외인비중: {col}', '%' if n else '원', 'legendonly' if m else True
                showlegend, dtype = True if n else False, 'float' if n else 'int'
                trace = traceLine(data=data, name=name, unit=unit, legendgroup=name, showlegend=showlegend, dtype=dtype)
                fig.add_trace(trace=trace, row=1, col=2, secondary_y=False if n else True)

        fig.update_layout(dict(title=f'{self.name}[{self.ticker}] : 수급 현황', plot_bgcolor='white'))
        fig.update_yaxes(title_text="주가[원]", showgrid=True, gridcolor='lightgrey', row=1, col=1)
        for row, col in ((1, 2), (2, 1), (2, 2)):
            fig.update_yaxes(title_text="주가[원]", showgrid=True, gridcolor='lightgrey', row=row, col=col,
                             secondary_y=True)
            fig.update_yaxes(title_text="비중[%]", showgrid=False, row=row, col=col, secondary_y=False)
        return fig


if __name__ == "__main__":
    from pykrx import stock as krx
    import random, os, datetime

    # tickers = krx.get_index_portfolio_deposit_file(ticker='1028')
    # ticker = random.sample(tickers, 1)[0]
    # ticker = 'COKE'
    ticker = '000240'

    t_analyze = analyze(ticker=ticker, period=3)
    print(t_analyze.name, ticker)

    # t_analyze.fig_pv.show()
    # t_analyze.fig_basic.show()
    # t_analyze.fig_bb.show()
    # t_analyze.fig_rsi.show()
    # t_analyze.fig_macd.show()
    # t_analyze.fig_cci.show()
    # t_analyze.fig_stc.show()
    # t_analyze.fig_trix.show()

    # t_analyze.fig_overview.show()


    path = rf'C:\Users\Administrator\Desktop\tdat\{datetime.datetime.today().strftime("%Y-%m-%d")}'
    if not os.path.isdir(path):
        os.makedirs(path)
    # t_analyze.save(t_analyze.fig_pv, title='가격', path=path)
    # t_analyze.save(t_analyze.fig_basic, title='직선추세', path=path)
    # t_analyze.save(t_analyze.fig_bb, title='볼린저밴드', path=path)
    # t_analyze.save(t_analyze.fig_macd, title='MACD', path=path)
    # t_analyze.save(t_analyze.fig_rsi, title='RSI', path=path)
    # t_analyze.save(t_analyze.fig_cci, title='CCI', path=path)
    # t_analyze.save(t_analyze.fig_stc, title='STC', path=path)
    # t_analyze.save(t_analyze.fig_trix, title='TRIX', path=path)
    # t_analyze.save(t_analyze.fig_vortex, title='VORTEX', path=path)

    t_analyze.save(t_analyze.fig_overview, title='Overview', path=path)
    t_analyze.save(t_analyze.fig_relative, title='Relative', path=path)
    t_analyze.save(t_analyze.fig_supply, title='Supply', path=path)