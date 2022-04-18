from tdatlib.viewer.common import (
    CD_COLORS,
    dform
)
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


def show_overview(
        ticker:str,
        name:str,
        df_products:pd.DataFrame,
        df_multifactor:pd.DataFrame,
        df_asset:pd.DataFrame,
        df_profit:pd.DataFrame
) -> go.Figure:

    fig = make_subplots(
        rows=2, cols=2, vertical_spacing=0.12, horizontal_spacing=0.1,
        subplot_titles=("제품 구성", "멀티 팩터", "자산", "연간 실적"),
        specs=[[{"type": "pie"}, {"type": "polar"}], [{"type": "bar"}, {"type": "bar"}]]
    )

    fig.add_trace(go.Pie(
        name='Product', labels=df_products.index, values=df_products, visible=True, showlegend=False,
        textinfo='label+percent', insidetextorientation='radial', hoverinfo='label+percent'
    ), row=1, col=1)

    for n, col in enumerate(df_multifactor.columns):
        fig.add_trace(go.Scatterpolar(
            name=col, r=df_multifactor[col], theta=df_multifactor.index, visible=True, showlegend=True,
            fill='toself', hovertemplate=col + '<br>팩터: %{theta}<br>값: %{r}<extra></extra>'
        ), row=1, col=2)

    fig.add_trace(go.Bar(
        name='자산', x=df_asset.index, y=df_asset.자산총계, marker=dict(color='green'), opacity=0.9,
        text=df_asset.자산총계LB, meta=df_asset.부채총계LB, customdata=df_asset.자본총계LB,
        visible=True, showlegend=False, offsetgroup=0, texttemplate='',
        hovertemplate='자산: %{text}<br>부채: %{meta}<br>자본: %{customdata}<extra></extra>'
    ), row=2, col=1)
    fig.add_trace(go.Bar(
        name='부채', x=df_asset.index, y=df_asset.부채총계, marker=dict(color='red'), opacity=0.8,
        visible=True, showlegend=False, offsetgroup=0, hoverinfo='skip'
    ), row=2, col=1)

    for n, col in enumerate(df_profit.columns):
        if col.endswith('LB'):
            continue

        fig.add_trace(go.Bar(
            name=f'연간{col}', x=df_profit.index, y=df_profit[col],
            marker=dict(color=CD_COLORS[n]), opacity=0.9, legendgroup=col, meta=df_profit[f'{col}LB'],
            hovertemplate=col + ': %{meta}<extra></extra>',
        ), row=2, col=2)

    fig.update_layout(dict(
        title=f'{name}[{ticker}] : 제품, 자산 및 실적',
        plot_bgcolor='white',
        margin=dict(l=0)
    ))
    fig.update_yaxes(title_text="억원", gridcolor='lightgrey', row=2, col=1)
    fig.update_yaxes(title_text="억원", gridcolor='lightgrey', row=2, col=2)
    for n, annotation in enumerate(fig['layout']['annotations']):
        annotation['x'] = 0 + 0.55 * (n % 2)
        annotation['xanchor'] = 'center'
        annotation['xref'] = 'paper'
    return fig


def show_relative(
        ticker:str,
        name:str,
        df_benchmark_return:pd.DataFrame,
        df_benchmark_multiple:pd.DataFrame
) -> go.Figure:

    fig = make_subplots(
        rows=2, cols=2, vertical_spacing=0.12, horizontal_spacing=0.1,
        subplot_titles=("상대 수익률", "PER", "EV/EBITA", "ROE"),
        specs=[[{"type": "xy"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]]
    )

    for col in ['3M', '1Y']:
        df = df_benchmark_return[col].dropna()
        for n, c in enumerate(df.columns):
            fig.add_trace(go.Scatter(
                name=f'{col}수익률비교', x=df.index, y=df[c].astype(float),
                visible=True if col == '3M' else 'legendonly', showlegend=True if not n else False,
                legendgroup=f'{col}수익률비교', meta=dform(span=df.index),
                hovertemplate='날짜: %{meta}<br>' + f'{c}: ' + '%{y:.2f}%<extra></extra>'
            ), row=1, col=1)

    for m, col in enumerate(['PER', 'EV/EBITDA', 'ROE']):
        df = df_benchmark_multiple[col]
        unit = '%' if col == 'ROE' else ''
        for n, c in enumerate(df.columns):
            fig.add_trace(go.Bar(
                name=f'{col}:{c}', x=df[c].index, y=df[c], marker=dict(color=CD_COLORS[n]),
                hovertemplate='분기: %{x}<br>' + c + ': %{y:.2f}' + unit + '<extra></extra>'
            ), row=1 if not m else 2, col=2 if m == 0 or m == 2 else 1)

    fig.update_layout(dict(
        title=f'<b>{name}[{ticker}]</b> : 벤치마크 대비 지표',
        plot_bgcolor='white',
    ))
    fig.update_yaxes(title_text="상대 수익률[%]", gridcolor='lightgrey', row=1, col=1)
    fig.update_yaxes(title_text="PER[-]", gridcolor='lightgrey', row=1, col=2)
    fig.update_yaxes(title_text="EV/EBITDA[-]", gridcolor='lightgrey', row=2, col=1)
    fig.update_yaxes(title_text="ROE[%]", gridcolor='lightgrey', row=2, col=2)
    fig.update_xaxes(gridcolor='lightgrey')
    for n, annotation in enumerate(fig['layout']['annotations']):
        annotation['x'] = 0 + 0.55 * (n % 2)
        annotation['xanchor'] = 'center'
        annotation['xref'] = 'paper'
    return fig


def show_supply(
        ticker:str,
        name:str,
        df_consensus:pd.DataFrame,
        df_foreign_rate:pd.DataFrame,
        df_short_sell:pd.DataFrame,
        df_short_balance:pd.DataFrame
) -> go.Figure:

    fig = make_subplots(
        rows=2, cols=2, vertical_spacing=0.11, horizontal_spacing=0.1,
        subplot_titles=("컨센서스", "외국인 보유비중", "차입공매도 비중", "대차잔고 비중"),
        specs=[[{"type": "xy"}, {"type": "xy", "secondary_y": True}],
               [{"type": "xy", "secondary_y": True}, {"type": "xy", 'secondary_y': True}]]
    )

    fig.add_trace(go.Scatter(
        name='목표주가', x=df_consensus.index, y=df_consensus.목표주가, mode='lines',
        legendgroup='컨센서스', legendgrouptitle=dict(text="컨센서스"),
        visible=True, showlegend=True, meta=dform(span=df_consensus.index),
        hovertemplate='날짜: %{meta}<br>목표주가: %{y:,}원<extra></extra>'
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        name='종가', x=df_consensus.index, y=df_consensus.종가, mode='lines',
        legendgroup='컨센서스',
        visible=True, showlegend=True, meta=dform(span=df_consensus.index),
        hovertemplate='날짜: %{meta}<br>종가: %{y:,}원<extra></extra>'
    ), row=1, col=1)

    df = df_foreign_rate[df_foreign_rate != '']['3M'].dropna()
    for n, c in enumerate(df.columns):
        form, name = '%{y:.2f}%' if n else '%{y:,d}원', '종가' if c.endswith('종가') else '비중'
        fig.add_trace(go.Scatter(
            name=f'3M: {name}', x=df.index, y=df[c], mode='lines', meta=dform(df.index), visible=True,
            showlegend=True, legendgroup='외국인 보유비중', legendgrouptitle=dict(text="외국인 보유비중"),
            hovertemplate='날짜: %{meta}<br>' + f'{name}: ' + f'{form}<extra></extra>'
        ), row=1, col=2, secondary_y=False if n else True)
    df = df_foreign_rate[df_foreign_rate != '']['1Y'].dropna()
    for n, c in enumerate(df.columns):
        form, name = '%{y:.2f}%' if n else '%{y:,d}원', '종가' if c.endswith('종가') else '비중'
        fig.add_trace(go.Scatter(
            name=f'1Y: {name}', x=df.index, y=df[c], mode='lines', meta=dform(df.index),
            visible='legendonly', showlegend=True, legendgroup='외국인 보유비중',
            hovertemplate='날짜: %{meta}<br>' + f'{name}: ' + f'{form}<extra></extra>'
        ), row=1, col=2, secondary_y=False if n else True)
    df = df_foreign_rate[df_foreign_rate != '']['3Y'].dropna()
    for n, c in enumerate(df.columns):
        form, name = '%{y:.2f}%' if n else '%{y:,d}원', '종가' if c.endswith('종가') else '비중'
        fig.add_trace(go.Scatter(
            name=f'3Y: {name}', x=df.index, y=df[c], mode='lines', meta=dform(df.index),
            visible='legendonly', showlegend=True, legendgroup='외국인 보유비중',
            hovertemplate='날짜: %{meta}<br>' + f'{name}: ' + f'{form}<extra></extra>'
        ), row=1, col=2, secondary_y=False if n else True)

    fig.add_trace(go.Scatter(
        name='공매도비중', x=df_short_sell.index, y=df_short_sell.차입공매도비중, mode='lines', visible=True,
        showlegend=True, legendgroup='차입공매도 비중', legendgrouptitle=dict(text='차입공매도 비중'),
        meta=dform(df_short_sell.index), hovertemplate='날짜: %{meta}<br>비중: %{y:.2f}%<extra></extra>'
    ), row=2, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(
        name='수정종가', x=df_short_sell.index, y=df_short_sell.수정종가, mode='lines', visible=True,
        showlegend=True, legendgroup='차입공매도 비중',
        meta=dform(df_short_sell.index), hovertemplate='날짜: %{meta}<br>종가: %{y:,d}원<extra></extra>'
    ), row=2, col=1, secondary_y=True)

    fig.add_trace(go.Scatter(
        name='대차잔고비중', x=df_short_balance.index, y=df_short_balance.대차잔고비중, mode='lines', visible=True,
        showlegend=True, legendgroup='대차잔고 비중', legendgrouptitle=dict(text='대차잔고 비중'),
        meta=dform(df_short_balance.index), hovertemplate='날짜: %{meta}<br>비중: %{y:.2f}%<extra></extra>'
    ), row=2, col=2, secondary_y=False)
    fig.add_trace(go.Scatter(
        name='수정종가', x=df_short_balance.index, y=df_short_balance.수정종가, mode='lines', visible=True,
        showlegend=True, legendgroup='대차잔고 비중',
        meta=dform(df_short_balance.index), hovertemplate='날짜: %{meta}<br>종가: %{y:,d}원<extra></extra>'
    ), row=2, col=2, secondary_y=True)

    fig.update_layout(
        title=f'{name}[{ticker}] : 수급 현황',
        plot_bgcolor='white',
        legend = dict(groupclick="toggleitem")
    )
    fig.update_yaxes(title_text="주가[원]", showgrid=True, gridcolor='lightgrey', row=1, col=1)
    for row, col in ((1, 2), (2, 1), (2, 2)):
        fig.update_yaxes(title_text="주가[원]", showgrid=True, gridcolor='lightgrey', row=row, col=col,
                         secondary_y=True)
        fig.update_yaxes(title_text="비중[%]", showgrid=False, row=row, col=col, secondary_y=False)
    for n, annotation in enumerate(fig['layout']['annotations']):
        annotation['x'] = 0 + 0.55 * (n % 2)
        annotation['xanchor'] = 'center'
        annotation['xref'] = 'paper'
    return fig


class narrative:
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

        cost = self.expenses.copy()
        for n, col in enumerate(['매출원가율', '판관비율', 'R&D투자비중']):
            df = cost[col].dropna().astype(float) if n < 2 else cost[col].fillna(0).astype(float)
            fig.add_trace(go.Bar(
                x=df.index, y=df, name=col,
                hovertemplate='%{x}<br>' + col + ': %{y:.2f}%<extra></extra>'
            ), row = n // 2 + 1, col=n % 2 + 1)

        a_stat = self.stat_annual.copy()
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

        multiples = self.multiple_series.copy()
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