from tdatlib.viewer.tools import CD_X_RANGER, dform, set_x, set_y
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


def object_candle(ohlcv:pd.DataFrame) -> go.Candlestick:
    return go.Candlestick(
        name='일봉', x=ohlcv.index, visible=True, showlegend=True, legendgrouptitle=dict(text='캔들차트'),
        open=ohlcv.시가, high=ohlcv.고가, low=ohlcv.저가, close=ohlcv.종가,
        increasing_line=dict(color='red'), decreasing_line=dict(color='royalblue')
    )

def object_volume(ohlcv:pd.DataFrame) -> go.Bar:
    return go.Bar(
        name='거래량', x=ohlcv.index, y=ohlcv.거래량, visible=True, showlegend=False,
        marker=dict(color=['blue' if d < 0 else 'red' for d in ohlcv.거래량.pct_change().fillna(1)]),
        meta=dform(span=ohlcv.index), hovertemplate='날짜:%{meta}<br>거래량:%{y:,d}<extra></extra>'
    )

def object_prices(ohlcv:pd.DataFrame, currency:str='KRW') -> list:
    meta, prices = dform(ohlcv.index), list()
    for i, n in enumerate(['시가', '고가', '저가', '종가']):
        scatter = go.Scatter(
            name=n, x=ohlcv.index, y=ohlcv[n], visible='legendonly', showlegend=True, meta=meta,
            hovertemplate='날짜: %{meta}<br>' + n + ': %{y:,}' + f'{currency}<extra></extra>'
        )
        if not i:
            scatter.legendgrouptitle = dict(text='주가 차트')
        prices.append(scatter)
    return prices

def object_bollinger_band(ta:pd.DataFrame) -> list:
    bb = list()
    for i, (df, n) in enumerate([(ta.volatility_bbh, '상한'), (ta.volatility_bbm, '기준'), (ta.volatility_bbl, '하한')]):
        scatter = go.Scatter(
            name='볼린저밴드', x=df.index, y=df, visible=True, meta=dform(df.index),
            mode='lines', line=dict(color='rgb(184, 247, 212)'), fill='tonexty' if i else None,
            showlegend=False if i else True, legendgroup='볼린저밴드',
            hovertemplate=n + '<br>날짜: %{meta}<br>값: %{y:,d}원<extra></extra>',
        )
        if not i:
            scatter.legendgrouptitle = dict(text='볼린저밴드')
        bb.append(scatter)
    return bb

def object_base(
        row_width:list,
        vertical_spacing:float,
        candle:go.Candlestick,
        volume:go.Bar,
        prices:list,
        bollinger:list,
        currency=str
) -> go.Figure:

    rows = len(row_width)
    fig = make_subplots(rows=rows, cols=1, row_width=row_width, shared_xaxes=True, vertical_spacing=vertical_spacing)
    fig.add_trace(trace=candle, row=1, col=1)
    _ = [fig.add_trace(trace=trace, row=1, col=1) for trace in prices]
    _ = [fig.add_trace(trace=trace, row=1, col=1) for trace in bollinger]
    fig.add_trace(trace=volume, row=2, col=1)

    title, label = '날짜' if rows == 2 else '', True if rows == 2 else False
    fig.update_layout(go.Layout(
        plot_bgcolor='white',
        xaxis=dict(
            title='', showgrid=True, gridcolor='lightgrey', showticklabels=False, zeroline=False, autorange=True,
            showline=True, linewidth=1, linecolor='grey', mirror=False, rangeselector=CD_X_RANGER
        ),
        yaxis=dict(
            title=currency, showgrid=True, gridcolor='lightgrey', showticklabels=True, zeroline=False, autorange=True,
            showline=True, linewidth=0.5, linecolor='grey', mirror=False
        ),
        xaxis2=dict(
            title=title, showgrid=True, gridcolor='lightgrey', showticklabels=label, zeroline=False, autorange=True,
            showline=True, linewidth=0.5, linecolor='grey', mirror=False
        ),
        yaxis2=dict(
            title='거래량', showgrid=True, gridcolor='lightgrey', showticklabels=True, zeroline=False, autorange=True,
            showline=True, linewidth=0.5, linecolor='grey', mirror=False
        ),
        xaxis_rangeslider=dict(visible=False)
    ))
    return fig


def show_basic(
        ticker:str,
        name:str,
        currency:str,
        base:go.Figure,
        sma:pd.DataFrame,
        trend:pd.DataFrame,
        bound:pd.DataFrame
) -> go.Figure:

    meta = dform(sma.index)
    for n, col in enumerate(sma.columns):
        line = go.Scatter(
            name=col, x=sma.index, y=sma[col], visible='legendonly', showlegend=True, meta=meta,
            hovertemplate='날짜: %{meta}<br>' + col + '%{y:,.2f}원<extra></extra>'
        )
        if not n:
            line.legendgrouptitle=dict(text='이동평균선')
        base.add_trace(line, row=1, col=1)

    for n, gap in enumerate(['2M', '3M', '6M', '1Y']):
        average = go.Scatter(
            name=f'{gap}평균추세', x=trend.index, y=trend[gap], mode='lines', visible='legendonly',
            showlegend=True, line=dict(dash='dash', color='grey'), hovertemplate='%{y:.2f}' + currency + '<extra></extra>'
        )
        if not n:
            average.legendgrouptitle = dict(text='평균추세')
        base.add_trace(average)

    for n, gap in enumerate(['2M', '3M', '6M', '1Y']):
        resist = go.Scatter(
            name=f'{gap}경계선', x=bound.index, y=bound[gap]['resist'], mode='lines', visible='legendonly',
            showlegend=True, legendgroup=gap,
            line=dict(dash='dot', color='blue'), hovertemplate='%{y:.2f}' + currency + '<extra></extra>'
        )
        if not n:
            resist.legendgrouptitle = dict(text='지지/저항선')
        base.add_trace(resist)

        resist = go.Scatter(
            name=f'{gap}경계선', x=bound.index, y=bound[gap]['support'], mode='lines', visible='legendonly',
            showlegend=False, legendgroup=gap,
            line=dict(dash='dot', color='red'), hovertemplate='%{y:.2f}' + currency + '<extra></extra>'
        )
        base.add_trace(resist)

    base.update_layout(
        title=f'{name}({ticker}) 기본 분석형 차트',
        # legend=dict(groupclick="toggleitem")
    )
    return base

def show_bollinger_band(
        ticker:str,
        name:str,
        base:go.Figure,
        ta:pd.DataFrame
) -> go.Figure:

    base.add_trace(go.Scatter(
        name='밴드폭', x=ta.index, y=ta.volatility_bbw, visible=True, showlegend=True, meta=dform(ta.index),
        hovertemplate='날짜: %{meta}<br>밴드폭: %{y:.2f}%<extra></extra>'
    ), row=3, col=1)
    base.add_trace(go.Scatter(
        name='신호', x=ta.index, y=ta.volatility_bbp, visible=True, showlegend=True, meta=dform(ta.index),
        hovertemplate='날짜: %{meta}<br>신호: %{y:.2f}<extra></extra>'
    ), row=4, col=1)

    base.update_layout(
        title=f'{name}({ticker}) 볼린저밴드',
        xaxis3=set_x(title=str(), label=False), yaxis3=set_y(title='폭[%]'),
        xaxis4=set_x(title='날짜', label=True), yaxis4=set_y(title='신호[-]')
    )
    return base

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

