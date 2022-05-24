from tdatlib.viewer.tools import CD_X_RANGER, dform, set_x, set_y
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


def show_rsi(
        ticker:str,
        name:str,
        base:go.Figure,
        ta:pd.DataFrame
) -> go.Figure:

    meta = dform(ta.index)
    base.add_trace(go.Scatter(
        name='RSI', x=ta.index, y=ta.momentum_rsi, visible=True, showlegend=True, legendgrouptitle=dict(text='RSI'),
        meta=meta, hovertemplate='날짜: %{meta}<br>RSI: %{y:.2f}%<extra></extra>'
    ), row=3, col=1)
    base.add_hrect(y0=70, y1=80, line_width=0, fillcolor='red', opacity=0.2, row=3, col=1)
    base.add_hrect(y0=20, y1=30, line_width=0, fillcolor='green', opacity=0.2, row=3, col=1)

    base.add_trace(go.Scatter(
        name='S-RSI', x=ta.index, y=ta.momentum_stoch, visible=True, showlegend=True, meta=meta,
        legendgrouptitle=dict(text='Stochastic-RSI'), hovertemplate='날짜: %{meta}<br>S-RSI: %{y:.2f}%<extra></extra>'
    ), row=4, col=1)
    base.add_trace(go.Scatter(
        name='S-RSI-Sig', x=ta.index, y=ta.momentum_stoch_signal, visible=True, showlegend=True, meta=meta,
        hovertemplate='날짜: %{meta}<br>S-RSI-Sig: %{y:.2f}%<extra></extra>'
    ), row=4, col=1)
    base.add_hrect(y0=80, y1=100, line_width=0, fillcolor='red', opacity=0.2, row=4, col=1)
    base.add_hrect(y0=0, y1=20, line_width=0, fillcolor='green', opacity=0.2, row=4, col=1)
    base.update_layout(
        title=f'{name}({ticker}) RSI',
        xaxis3=set_x(title=str(), label=False), yaxis3=set_y(title='RSI[%]'),
        xaxis4=set_x(title='날짜', label=True), yaxis4=set_y(title='S-RSI[%]'),
    )
    return base

def show_macd(
        ticker:str,
        name:str,
        base:go.Figure,
        ta:pd.DataFrame
) -> go.Figure:

    meta = dform(ta.index)
    base.add_trace(go.Scatter(
        name='MACD', x=ta.index, y=ta.trend_macd, visible=True, showlegend=True, meta=meta,
        legendgrouptitle=dict(text='MACD'), hovertemplate='날짜: %{meta}<br>MACD: %{y:.2f}<extra></extra>'
    ), row=3, col=1)

    base.add_trace(go.Scatter(
        name='Signal', x=ta.index, y=ta.trend_macd_signal, visible=True, showlegend=True, meta=meta,
        hovertemplate='날짜: %{meta}<br>Signal: %{y:.2f}<extra></extra>'
    ), row=3, col=1)

    data = ta.trend_macd_diff
    base.add_trace(go.Bar(
        name='Diff', x=data.index, y=data, visible=True, showlegend=False, meta=meta,
        marker=dict(color=['royalblue' if y < 0 else 'red' for y in data.pct_change().fillna(1)]),
        hovertemplate='날짜: %{meta}<br>Diff: %{y:.2f}<extra></extra>'
    ), row=3, col=1)
    base.add_hline(y=0, line_width=0.5, line_dash="dash", line_color="black", row=3, col=1)

    base.update_layout(
        title=f'{name}({ticker}) MACD',
        xaxis3=set_x(title='날짜', label=True), yaxis3=set_y(title='MACD')
    )
    return base

def show_mfi(
        ticker:str,
        name:str,
        base:go.Figure,
        ta:pd.DataFrame,
) -> go.Figure:

    base.add_trace(go.Scatter(
        name='MFI', x=ta.index, y=ta.volume_mfi, visible=True, showlegend=True, legendgrouptitle=dict(text='MFI'),
        meta=dform(ta.index), hovertemplate='날짜: %{meta}<br>MFI: %{y:.2f}%<extra></extra>'
    ), row=3, col=1)
    base.add_hrect(y0=80, y1=100, line_width=0, fillcolor='red', opacity=0.2, row=3, col=1)
    base.add_hline(y=90, line_width=0.5, line_dash="dash", line_color="black", row=3, col=1)
    base.add_hrect(y0=0, y1=20, line_width=0, fillcolor='lightgreen', opacity=0.4, row=3, col=1)
    base.add_hline(y=10, line_width=0.5, line_dash="dash", line_color="black", row=3, col=1)
    base.update_layout(
        title=f'{name}({ticker}) MFI',
        xaxis3=set_x(title='날짜', label=True), yaxis3=set_y(title='MFI'),
    )
    return base

def show_cci(
        ticker:str,
        name:str,
        base:go.Figure,
        ta:pd.DataFrame
) -> go.Figure:

    base.add_trace(go.Scatter(
        name='CCI', x=ta.index, y=ta.trend_cci, visible=True, showlegend=True, legendgrouptitle=dict(text='CCI'),
        meta=dform(ta.index), hovertemplate='날짜: %{meta}<br>CCI: %{y:.2f}%<extra></extra>'
    ), row=3, col=1)
    base.add_hrect(y0=200, y1=400, line_width=0, fillcolor='red', opacity=0.2, row=3, col=1)
    base.add_hrect(y0=100, y1=200, line_width=0, fillcolor='brown', opacity=0.2, row=3, col=1)
    base.add_hrect(y0=-200, y1=-100, line_width=0, fillcolor='lightgreen', opacity=0.4, row=3, col=1)
    base.add_hrect(y0=-400, y1=-200, line_width=0, fillcolor='green', opacity=0.2, row=3, col=1)
    base.update_layout(
        title=f'{name}({ticker}) CCI',
        xaxis3=set_x(title='날짜', label=True), yaxis3=set_y(title='CCI'),
    )
    return base

def show_vortex(
        ticker:str,
        name:str,
        base:go.Figure,
        ta:pd.DataFrame
) -> go.Figure:

    meta = dform(ta.index)
    base.add_trace(go.Scatter(
        name='V+', x=ta.index, y=ta.trend_vortex_ind_pos, visible=True, showlegend=True, legendgrouptitle=dict(text='Vortex'),
        meta=meta, hovertemplate='날짜: %{meta}<br>Vortex(+): %{y:.2f}<extra></extra>'
    ), row=3, col=1)
    base.add_trace(go.Scatter(
        name='V-', x=ta.index, y=ta.trend_vortex_ind_neg, visible=True, showlegend=True,
        meta=meta, hovertemplate='날짜: %{meta}<br>Vortex(-): %{y:.2f}<extra></extra>'
    ), row=3, col=1)
    base.add_trace(go.Scatter(
        name='Diff', x=ta.index, y=ta.trend_vortex_ind_diff, visible=True, showlegend=True,
        meta=meta, hovertemplate='날짜: %{meta}<br>V-Diff: %{y:.2f}<extra></extra>'
    ), row=4, col=1)

    base.add_hline(y=0, line_width=0.5, line_dash="dash", line_color="black", row=4, col=1)
    base.update_layout(
        title=f'{name}({ticker}) VORTEX',
        xaxis3=set_x(title=str(), label=False), yaxis3=set_y(title='VORTEX'),
        xaxis4=set_x(title='날짜', label=True), yaxis4=set_y(title='VORTEX-Sig'),
    )
    return base

def show_stc(
        ticker:str,
        name:str,
        base:go.Figure,
        ta:pd.DataFrame
) -> go.Figure:

    base.add_trace(go.Scatter(
        name='STC', x=ta.index, y=ta.trend_stc, visible=True, showlegend=True, legendgrouptitle=dict(text='STC'),
        meta=dform(ta.index), hovertemplate='날짜: %{meta}<br>STC: %{y:.2f}%<extra></extra>'
    ), row=3, col=1)

    base.update_layout(
        title=f'{name}({ticker}) STC',
        xaxis3=set_x(title='날짜', label=True), yaxis3=set_y(title='STC'),
    )
    return base

def show_trix(
        ticker:str,
        name:str,
        base:go.Figure,
        trix:pd.DataFrame
) -> go.Figure:

    meta = dform(trix.index)
    base.add_trace(go.Scatter(
        name='TRIX', x=trix.index, y=trix.trix, visible=True, showlegend=True, legendgrouptitle=dict(text='TRIX'),
        meta=meta, hovertemplate='날짜: %{meta}<br>TRIX: %{y:.2f}<extra></extra>'
    ), row=3, col=1)

    base.add_trace(go.Scatter(
        name='Signal', x=trix.index, y=trix.Signal, visible='legendonly', showlegend=True, mode='markers',
        marker=dict(
            symbol=['triangle-down' if s > 0 else 'triangle-up' for s in trix.Signal],
            color=['blue' if s > 0 else 'red' for s in trix.Signal],
            size=8
        ),
        meta=meta, hovertemplate='날짜: %{meta}<br>신호: %{y:.2f}<extra></extra>'
    ), row=3, col=1)

    base.add_trace(go.Scatter(
        name='Bottom', x=trix.index, y=trix.Bottom, visible='legendonly', showlegend=True, mode='markers',
        marker=dict(symbol='circle-open', color='green', size=8),
        meta=meta, hovertemplate='날짜: %{meta}<br>바닥: %{y:.2f}<extra></extra>'
    ), row=3, col=1)

    base.update_layout(
        title=f'{name}({ticker}) TRIX',
        xaxis3=set_x(title='날짜', label=True), yaxis3=set_y(title='TRIX'),
    )
    return base

def show_ta(
        name:str,
        ticker:str,
        base:go.Figure,
        ta:pd.DataFrame,
        indicator:str
) -> go.Figure:

    scatter = go.Scatter(
        name=indicator,
        x=ta.index,
        y=ta[indicator],
        visible=True,
        showlegend=True,
        hovertemplate='%{x}<br>' + indicator + ': %{y:.2f}<extra></extra>'
    )
    base.add_trace(scatter, row=3, col=1)
    base.update_layout(
        title=f'{name}({ticker}) {indicator}',
        xaxis3=dict(
            title='날짜',
            showgrid=True,
            gridcolor='lightgrey',
            autorange=True,
            tickformat='%Y/%m/%d',
        ),
        yaxis3=dict(
            title=f'{indicator}',
            showgrid=True,
            gridcolor='lightgrey',
            autorange=True
        )
    )
    return base

