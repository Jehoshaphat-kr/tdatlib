from tdatlib.view.stock.toolbox import *
from tdatlib import kr_fundamental
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as of


class fundamental(kr_fundamental):

    def __init__(self, ticker:str, name:str=str()):
        super().__init__(ticker=ticker, name=name)
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
        fa = fig.add_trace

        product, a_stat = self.product.copy(), self.annual_statement.copy()
        fa(go.Pie(
            name='Product', labels=product.index, values=product,
            visible=True, showlegend=False,
            textinfo='label+percent', insidetextorientation='radial', hoverinfo='label+percent'
        ), row=1, col=1)

        multi_factor = self.multi_factor.copy()
        for n, col in enumerate(multi_factor.columns):
            fa(go.Scatterpolar(
                name=col, r=multi_factor[col].astype(float), theta=multi_factor.index,
                visible=True, showlegend=True,
                fill='toself', hovertemplate=col + '<br>팩터: %{theta}<br>값: %{r}<extra></extra>'
            ), row=1, col=2)

        asset = a_stat[['자산총계', '부채총계', '자본총계']].fillna(0).astype(int).copy()
        c2t = lambda x: str(x) if x < 10000 else f'{str(x)[:-4]}조 {str(x)[-4:]}억원'
        fa(go.Bar(
            name='자산', x=asset.index, y=asset.자산총계, marker=dict(color='green'), opacity=0.9,
            text=asset.자산총계.apply(c2t), meta=asset.부채총계.apply(c2t), customdata=asset.자본총계.apply(c2t),
            visible=True, showlegend=False, offsetgroup=0, texttemplate='',
            hovertemplate='자산: %{text}<br>부채: %{meta}<br>자본: %{customdata}<extra></extra>'
        ), row=2, col=1)
        fa(go.Bar(
            name='부채', x=asset.index, y=asset.부채총계, marker=dict(color='red'), opacity=0.8,
            visible=True, showlegend=False, offsetgroup=0, hoverinfo='skip'
        ), row=2, col=1)

        key = [_ for _ in ['매출액', '순영업수익', '이자수익', '보험료수익'] if _ in a_stat.columns][0]
        require = a_stat[[key, '영업이익', '당기순이익']]
        for n, col in enumerate(require.columns):
            y = require[col].fillna(0).astype(int)
            fa(go.Bar(
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

        consen = self.consensus.copy()
        fig.add_trace(
            trace=traceLine(data=consen.목표주가.dropna(), name='컨센서스: 목표가', unit='원', dtype='int'),
            row=1, col=1
        )
        fig.add_trace(
            trace=traceLine(data=consen.종가, name='컨센서스: 종가', unit='원', dtype='int'),
            row=1, col=1
        )

        foreign = self.foreigner.copy()
        for m, col in enumerate(['3M', '1Y', '3Y']):
            df = foreign[col].dropna()
            df = df[df != '']
            for n, c in enumerate(df.columns):
                data = df[c].astype(float) if n else df[c].astype(int)
                name, unit, visible = f'외인비중: {col}' if n else '종가', '%' if n else '원', 'legendonly' if m else True
                showlegend, dtype = True if n else False, 'float' if n else 'int'
                trace = traceLine(
                    data=data, name=name, unit=unit, legendgroup=name, visible=visible, showlegend=showlegend, dtype=dtype
                )
                fig.add_trace(trace=trace, row=1, col=2, secondary_y=False if n else True)

        shorts = self.short.copy()
        for n, col in enumerate(shorts.columns):
            data = shorts[col].astype(int) if n else shorts[col].astype(float)
            name, unit = f'공매도: {col}' if n else col, '원' if n else '%'
            dtype, s_y = 'int' if n else 'float', True if n else False
            fig.add_trace(traceLine(data=data, name=name, unit=unit, dtype=dtype), row=2, col=1, secondary_y=s_y)

        balance = self.short_balance.copy()
        for n, col in enumerate(balance.columns):
            data = balance[col].astype(int) if n else balance[col].astype(float)
            name, unit, showlegend = col if n else col, '원' if n else '%', False if n else True
            dtype, s_y = 'int' if n else 'float', True if n else False
            fig.add_trace(
                trace=traceLine(data=data, name=name, unit=unit, dtype=dtype, showlegend=showlegend),
                row=2, col=2, secondary_y=s_y
            )

        fig.update_layout(dict(title=f'{self.name}[{self.ticker}] : 수급 현황', plot_bgcolor='white'))
        fig.update_yaxes(title_text="주가[원]", showgrid=True, gridcolor='lightgrey', row=1, col=1)
        for row, col in ((1, 2), (2, 1), (2, 2)):
            fig.update_yaxes(title_text="주가[원]", showgrid=True, gridcolor='lightgrey', row=row, col=col,
                             secondary_y=True)
            fig.update_yaxes(title_text="비중[%]", showgrid=False, row=row, col=col, secondary_y=False)
        return fig

    @property
    def fig_cost(self) -> go.Figure:
        """
        지출 비용
        """
        fig = make_subplots(
            rows=2, cols=2, vertical_spacing=0.11, horizontal_spacing=0.1,
            subplot_titles=("매출 원가", "판관비", "R&D투자 비중", "부채율"),
            specs=[[{"type": "xy", "secondary_y": True}, {"type": "xy", "secondary_y": True}],
                   [{"type": "xy", "secondary_y": True}, {"type": "xy", 'secondary_y': True}]]
        )

        cost = self.cost.copy()
        for n, col in enumerate(['매출원가율', '판관비율', 'R&D투자비중']):
            df = cost[col].dropna().astype(float) if n < 2 else cost[col].fillna(0).astype(float)
            fig.add_trace(go.Bar(
                x=df.index, y=df, name=col,
                hovertemplate='%{x}<br>' + col + ': %{y:.2f}%<extra></extra>'
            ), row = n // 2 + 1, col=n % 2 + 1)

        a_stat = self.annual_statement.copy()
        fig.add_trace(go.Bar(
            x=a_stat.index, y=a_stat['부채비율'].astype(float), name='부채비율',
            hovertemplate='%{x}<br>부채비율: %{y:.2f}%<extra></extra>'
       ), row=2, col=2)

        fig.update_layout(dict(title=f'{self.name}[{self.ticker}]: 비용과 부채', plot_bgcolor='white'))
        for row, col in ((1, 1), (1, 2), (2, 1), (2, 2)):
            fig.update_yaxes(title_text="비율[%]", showgrid=True, gridcolor='lightgrey', row=row, col=col)
        return fig

    @property
    def fig_multiple(self) -> go.Figure:
        """

        """
        fig = make_subplots(
            rows=2, cols=2, vertical_spacing=0.11, horizontal_spacing=0.1,
            subplot_titles=("EPS / PER(3Y)", "BPS / PBR(3Y)", "PER BAND", "PBR BAND"),
            specs=[[{"type": "xy", "secondary_y": True}, {"type": "xy", "secondary_y": True}],
                   [{"type": "xy", "secondary_y": False}, {"type": "xy", 'secondary_y': False}]]
        )
        fa = fig.add_trace

        multiples = self.multiples.copy()
        for n, c in enumerate(['PER', 'EPS']):
            data, dtype, unit = multiples[c].astype(int if n else float), 'int' if n else 'float', '원' if n else ''
            fa(trace=traceLine(data=data, name=c, unit=unit, dtype=dtype), row=1, col=1, secondary_y=False if n else True)
        for n, c in enumerate(['PBR', 'BPS']):
            data, dtype, unit = multiples[c].astype(int if n else float), 'int' if n else 'float', '원' if n else ''
            fa(trace=traceLine(data=data, name=c, unit=unit, dtype=dtype), row=1, col=2, secondary_y=False if n else True)

        per, pbr = self.multiple_band
        for n, c in enumerate(per.columns):
            data, dtype, unit = per[c].dropna().astype(float if n else int), 'float' if n else 'int', '' if n else '원'
            fa(trace=traceLine(data=data, name=c, unit=unit, dtype=dtype), row=2, col=1)
        for n, c in enumerate(pbr.columns):
            data, dtype, unit = pbr[c].dropna().astype(float if n else int), 'float' if n else 'int', '' if n else '원'
            fa(trace=traceLine(data=data, name=c, unit=unit, dtype=dtype), row=2, col=2)

        fig.update_layout(dict(
            title=f'<b>{self.name}[{self.ticker}]</b> : PER / PBR',
            plot_bgcolor='white'
        ))
        for row, col in ((1, 1), (1, 2), (2, 1), (2, 2)):
            fig.update_yaxes(title_text="KRW[원]", showgrid=True, gridcolor='lightgrey', row=row, col=col,
                             secondary_y=False)
            fig.update_yaxes(title_text="배수[-]", showgrid=False, row=row, col=col, secondary_y=True)
        return fig


if __name__ == "__main__":
    from tdatlib import archive
    from pykrx import stock as krx
    import random, os, datetime

    tickers = krx.get_index_portfolio_deposit_file(ticker='1028')
    ticker = random.sample(tickers, 1)[0]
    # ticker = 'COKE'
    # ticker = '093370'

    t_analyze = fundamental(ticker=ticker)
    print(t_analyze.name, ticker)

    # t_analyze.fig_overview.show()
    # t_analyze.fig_multiple.show()


    path = os.path.join(archive.desktop, f'tdat/{datetime.datetime.today().strftime("%Y-%m-%d")}')
    if not os.path.isdir(path):
        os.makedirs(path)

    t_analyze.save(t_analyze.fig_overview, title='Overview', path=path)
    t_analyze.save(t_analyze.fig_relative, title='Relative', path=path)
    t_analyze.save(t_analyze.fig_supply, title='Supply', path=path)
    t_analyze.save(t_analyze.fig_cost, title='Cost', path=path)
    t_analyze.save(t_analyze.fig_multiple, title='Multiples', path=path)