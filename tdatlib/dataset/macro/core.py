from pandas_datareader import get_data_fred as fred
from datetime import datetime, timedelta
import pandas as pd


US기준금리 = 'EFFR'
US10년물금리 = 'T10YFF'
US5년기대인플레 = 'T5YIFR'
US소비자물가지수 = 'CPIAUCSL'
US10년평형인플레 = 'T10YIE'
TODAY = datetime.now().date()


basis = US10년물금리

period = 10
raw = fred(
    symbols=basis,
    start=TODAY - timedelta(period * 365),
    end=TODAY
)
# raw = raw.astype(float)

if __name__ == "__main__":
    from tdatlib.tdef import *
    from tdatlib.dataset import stock
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    import plotly.offline as of
    import os

    compare = KB금융

    _stock = stock.KR(ticker=compare, period=10)
    price = _stock.ohlcv

    data = pd.concat(objs=[raw, price], axis=1)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Candlestick(
            name=compare,
            x=_stock.ohlcv.index,
            open=_stock.ohlcv.시가,
            high=_stock.ohlcv.고가,
            low=_stock.ohlcv.저가,
            close=_stock.ohlcv.종가,
            visible=True,
            showlegend=True,
            legendgrouptitle=dict(text='캔들 차트'),
            increasing_line=dict(color='red'),
            decreasing_line=dict(color='royalblue'),
            xhoverformat='%Y/%m/%d',
            yhoverformat=',' if _stock.currency == '원' else '.2f',
        ), secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=raw.index,
            y=raw[basis],
            name=basis,
            mode='lines',
            visible=True,
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            yhoverformat='.2f'
        ), secondary_y=True
    )

    fig.update_layout(
        # title=f'{self.tag} Trix',
        plot_bgcolor='white',
        xaxis_rangeslider=dict(visible=False),
        xaxis=dict(
            showticklabels=False,
            tickformat='%Y/%m/%d',
            zeroline=False,
            showgrid=True,
            gridcolor='lightgrey',
            autorange=True,
            showline=True,
            linewidth=1,
            linecolor='grey',
            mirror=False,
        ),
        yaxis=dict(
            showticklabels=True,
            zeroline=False,
            showgrid=True,
            gridcolor='lightgrey',
            autorange=True,
            showline=True,
            linewidth=0.5,
            linecolor='grey',
            mirror=False
        )
    )

    # noinspection PyBroadException
    try:
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    except:
        desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')

    path = f'{desktop}/tdat/{datetime.now().strftime("%Y-%m-%d")}/MACRO'
    if not os.path.isdir(path):
        os.makedirs(path)
    of.plot(fig, filename=f'{path}/TEST.html', auto_open=False)


