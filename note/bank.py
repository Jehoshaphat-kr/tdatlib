from tdatlib import macro, market, index, stock
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


"""
분석 객체
"""
market = market.KR()

TICKERS = pd.DataFrame(
    data=[
        dict(ticker="5046",   종류="지수", 이름="KRX은행"),
        dict(ticker="091170", 종류="ETF", 이름="KODEX은행"),
        dict(ticker="091220", 종류="ETF", 이름="TIGER은행"),
        dict(ticker="105560", 종류="주식", 이름="KB금융"),
        dict(ticker="086790", 종류="주식", 이름="하나금융지주"),
        dict(ticker="139130", 종류="주식", 이름="DGB금융지주"),
        dict(ticker="055550", 종류="주식", 이름="신한지주"),
        dict(ticker="024110", 종류="주식", 이름="기업은행"),
        dict(ticker="138930", 종류="주식", 이름="BNK금융지주"),
        dict(ticker="316140", 종류="주식", 이름="우리금융지주"),
        dict(ticker="038540", 종류="주식", 이름="상상인"),
    ]
).set_index(keys='ticker').join(other=market.icm)


"""
은행 사업 구조 파악(매출 기준)
"""
target = TICKERS.sort_values(by='시가총액', ascending=False)[:4]
fig = make_subplots(
    rows=2,
    cols=2,
    vertical_spacing=0.12,
    horizontal_spacing=0.1,
    subplot_titles=tuple(target.이름.tolist()),
    specs=[
        [{"type": "pie"}, {"type": "pie"}],
        [{"type": "pie"}, {"type": "pie"}]
    ]
)

for n, ticker in enumerate(target.index):
    kr = stock.kr(ticker=ticker)
    products = kr.fnguide.Products
    fig.add_trace(
        trace = go.Pie(
            name='Product',
            labels=products.index,
            values=products,
            visible=True,
            showlegend=False,
            textfont=dict(color='white'),
            textinfo='label+percent',
            insidetextorientation='radial',
            hoverinfo='label+percent'
        ), row = n // 2 + 1, col = n % 2 + 1
    )

fig.update_layout(dict(
    title=f'<b>은행주</b> 주요 매출처',
    plot_bgcolor='white',
))
fig.update_xaxes()
for n, annotation in enumerate(fig['layout']['annotations']):
    annotation['x'] = 0 + 0.55 * (n % 2)
    annotation['xanchor'] = 'center'
    annotation['xref'] = 'paper'
fig.show()

