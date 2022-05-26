from tdatlib.viewer.tools import (
    CD_COLORS,
    dform
)
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


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

    df = df_foreign_rate[df_foreign_rate != '']['3M'].dropna()
    for n, c in enumerate(df.columns):
        form, name = '%{y:.2f}%' if n else '%{y:,d}원', '종가' if c.endswith('종가') else '비중'
        fig.add_trace(go.Scatter(
            name=f'3개월:{name}', x=df.index, y=df[c], mode='lines', meta=dform(df.index), visible=True,
            showlegend=True, legendgroup='3개월', legendgrouptitle=dict(text="외국인 보유비중"),
            hovertemplate='날짜: %{meta}<br>' + f'{name}: ' + f'{form}<extra></extra>'
        ), row=1, col=2, secondary_y=False if n else True)
    df = df_foreign_rate[df_foreign_rate != '']['1Y'].dropna()
    for n, c in enumerate(df.columns):
        form, name = '%{y:.2f}%' if n else '%{y:,d}원', '종가' if c.endswith('종가') else '비중'
        fig.add_trace(go.Scatter(
            name=f'1년:{name}', x=df.index, y=df[c], mode='lines', meta=dform(df.index),
            visible='legendonly', showlegend=True, legendgroup='1년',
            hovertemplate='날짜: %{meta}<br>' + f'{name}: ' + f'{form}<extra></extra>'
        ), row=1, col=2, secondary_y=False if n else True)
    df = df_foreign_rate[df_foreign_rate != '']['3Y'].dropna()
    for n, c in enumerate(df.columns):
        form, name = '%{y:.2f}%' if n else '%{y:,d}원', '종가' if c.endswith('종가') else '비중'
        fig.add_trace(go.Scatter(
            name=f'3년: {name}', x=df.index, y=df[c], mode='lines', meta=dform(df.index),
            visible='legendonly', showlegend=True, legendgroup='3년',
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


def show_cost(
        ticker:str,
        name:str,
        df_expenses:pd.DataFrame,
        df_statement:pd.DataFrame
) -> go.Figure:

    fig = make_subplots(
        rows=2, cols=2, vertical_spacing=0.11, horizontal_spacing=0.1,
        subplot_titles=("매출 원가", "판관비", "R&D투자 비중", "부채율"),
        specs=[[{"type": "xy", "secondary_y": True}, {"type": "xy", "secondary_y": True}],
               [{"type": "xy", "secondary_y": True}, {"type": "xy", 'secondary_y': True}]]
    )

    for n, col in enumerate(['매출원가율', '판관비율', 'R&D투자비중']):
        df = df_expenses[col].dropna()
        fig.add_trace(go.Scatter(
            name=col, x=df.index, y=df, mode='lines+markers',
            hovertemplate='%{x}<br>' + col + ': %{y:.2f}%<extra></extra>'
        ), row = n // 2 + 1, col=n % 2 + 1)

    df = df_statement['부채비율'].dropna()
    fig.add_trace(go.Scatter(
        x=df.index, y=df, name='부채비율', mode='lines+markers',
        hovertemplate='%{x}<br>부채비율: %{y:.2f}%<extra></extra>'
   ), row=2, col=2)

    fig.update_layout(dict(title=f'{name}[{ticker}]: 비용과 부채', plot_bgcolor='white'))
    for row, col in ((1, 1), (1, 2), (2, 1), (2, 2)):
        fig.update_yaxes(title_text="비율[%]", showgrid=True, gridcolor='lightgrey', row=row, col=col)
    for n, annotation in enumerate(fig['layout']['annotations']):
        annotation['x'] = 0 + 0.55 * (n % 2)
        annotation['xanchor'] = 'center'
        annotation['xref'] = 'paper'
    return fig


def show_multiples(
        ticker:str,
        name:str,
        df_multiple_series:pd.DataFrame,
        df_multiple_band:pd.DataFrame
) -> go.Figure:

    fig = make_subplots(
        rows=2, cols=2, vertical_spacing=0.11, horizontal_spacing=0.1,
        subplot_titles=("EPS / PER(3Y)", "BPS / PBR(3Y)", "PER BAND", "PBR BAND"),
        specs=[[{"type": "xy", "secondary_y": True}, {"type": "xy", "secondary_y": True}],
               [{"type": "xy", "secondary_y": False}, {"type": "xy", 'secondary_y': False}]]
    )

    meta = dform(span=df_multiple_series.index)
    fig.add_trace(go.Scatter(
        name='PER', x=df_multiple_series.index, y=df_multiple_series.PER, visible=True, meta=meta,
        showlegend=True, legendgroup='PER_EPS', legendgrouptitle=dict(text='PER/EPS'),
        hovertemplate='날짜: %{meta}<br>PER: %{y:.2f}<extra></extra>'
    ), row=1, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(
        name='EPS', x=df_multiple_series.index, y=df_multiple_series.EPS, visible=True, meta=meta,
        showlegend=True, legendgroup='PER_EPS',
        hovertemplate='날짜: %{meta}<br>EPS: %{y:,d}원<extra></extra>'
    ), row=1, col=1, secondary_y=False)

    fig.add_trace(go.Scatter(
        name='PBR', x=df_multiple_series.index, y=df_multiple_series.PBR, visible=True, meta=meta,
        showlegend=True, legendgroup='PBR_BPS', legendgrouptitle=dict(text='PBR/BPS'),
        hovertemplate='날짜: %{meta}<br>PBR: %{y:.2f}<extra></extra>'
    ), row=1, col=2, secondary_y=True)
    fig.add_trace(go.Scatter(
        name='BPS', x=df_multiple_series.index, y=df_multiple_series.BPS, visible=True, meta=meta,
        showlegend=True, legendgroup='PBR_BPS',
        hovertemplate='날짜: %{meta}<br>BPS: %{y:,d}원<extra></extra>'
    ), row=1, col=2, secondary_y=False)

    per, pbr = df_multiple_band
    meta = dform(span=per.index)
    prc = per[per.columns[0]].dropna().astype(int)
    fig.add_trace(go.Scatter(
        name=per.columns[0], x=prc.index, y=prc, visible=True, meta=meta,
        showlegend=True, legendgroup='PER BAND', legendgrouptitle=dict(text='PER BAND'),
        hovertemplate='날짜: %{meta}<br>주가: %{y:,d}원<extra></extra>'
    ), row=2, col=1)
    for n, c in enumerate(per.columns[1:]):
        data = per[c].dropna().astype(float)
        fig.add_trace(go.Scatter(
            name=c, x=data.index, y=data, visible=True, meta=meta,
            showlegend=True, legendgroup='PER BAND',
            hovertemplate='날짜: %{meta}<br>' + c + ': %{y:,.2f}원<extra></extra>'
        ), row=2, col=1)

    meta = dform(span=pbr.index)
    prc = pbr[pbr.columns[0]].dropna().astype(int)
    fig.add_trace(go.Scatter(
        name=pbr.columns[0], x=prc.index, y=prc, visible=True, meta=meta,
        showlegend=True, legendgroup='PBR BAND', legendgrouptitle=dict(text='PBR BAND'),
        hovertemplate='날짜: %{meta}<br>주가: %{y:,d}원<extra></extra>'
    ), row=2, col=2)
    for n, c in enumerate(pbr.columns[1:]):
        data = pbr[c].dropna().astype(float)
        fig.add_trace(go.Scatter(
            name=c, x=data.index, y=data, visible=True, meta=meta,
            showlegend=True, legendgroup='PBR BAND',
            hovertemplate='날짜: %{meta}<br>' + c + ': %{y:,.2f}원<extra></extra>'
        ), row=2, col=2)


    fig.update_layout(dict(
        title=f'<b>{name}[{ticker}]</b> : PER / PBR',
        plot_bgcolor='white',
        legend=dict(groupclick="toggleitem")
    ))
    for row, col in ((1, 1), (1, 2), (2, 1), (2, 2)):
        fig.update_yaxes(title_text="KRW[원]", showgrid=True, gridcolor='lightgrey', row=row, col=col, secondary_y=False)
        fig.update_yaxes(title_text="배수[-]", showgrid=False, row=row, col=col, secondary_y=True)
    for n, annotation in enumerate(fig['layout']['annotations']):
        annotation['x'] = 0 + 0.55 * (n % 2)
        annotation['xanchor'] = 'center'
        annotation['xref'] = 'paper'
    return fig