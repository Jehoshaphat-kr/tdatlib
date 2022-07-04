from pandas_datareader import get_data_fred as fred
from datetime import datetime, timedelta
import pandas as pd
import requests


def fetch_fred(symbols:str or list, period:int = 10):
    today = datetime.now().date()
    start = today - timedelta(period * 365)
    end = today
    return fred(symbols=symbols, start=start, end=end)


def fetch_kr():
    url = "http://ecos.bok.or.kr/api/KeyStatisticList/XT2S2EESV0C0728KFJBT/json/kr/1/100/"
    resp = requests.get(url)
    data = resp.json()
    return data


if __name__ == "__main__":

    data = fetch_kr()
    frm = pd.DataFrame(data['KeyStatisticList']['row'])
    file = open('./raw.txt', 'w')
    file.write(str(data))
    file.close()
    # print(frm)
    # frm.to_csv('./test.csv', encoding='euc-kr', index=False)

    # from tdatlib.tdef import labels
    # from tdatlib.dataset import stock
    # from plotly.subplots import make_subplots
    # import plotly.graph_objects as go
    # import plotly.offline as of
    # import os
    #
    # save_filename = '환율'
    # basis = labels.KR수출량
    # compare = labels.KRX은행
    # period = 10
    #
    # _basis = fetch_fred(symbols=basis, period=period)
    #
    # _stock = stock.KR(ticker=compare, period=period)
    # price = _stock.ohlcv
    #
    # data = pd.concat(
    #     objs=[
    #         _basis,
    #         price
    #     ],
    #     axis=1
    # )
    # corr = data[[basis, '종가']].corr()
    # r_sq = corr.iloc[0, 1] ** 2
    # print(corr)
    # print(r_sq)
    #
    # fig = make_subplots(specs=[[{"secondary_y": True}]])
    #
    # fig.add_trace(
    #     go.Candlestick(
    #         name=_stock.label,
    #         x=_stock.ohlcv.index,
    #         open=_stock.ohlcv.시가,
    #         high=_stock.ohlcv.고가,
    #         low=_stock.ohlcv.저가,
    #         close=_stock.ohlcv.종가,
    #         visible=True,
    #         showlegend=True,
    #         legendgrouptitle=dict(text='캔들 차트'),
    #         increasing_line=dict(color='red'),
    #         decreasing_line=dict(color='royalblue'),
    #         xhoverformat='%Y/%m/%d',
    #         yhoverformat=',' if _stock.currency == '원' else '.2f',
    #     ), secondary_y=False
    # )
    #
    # fig.add_trace(
    #     go.Scatter(
    #         x=_basis.index,
    #         y=_basis[basis],
    #         name=basis,
    #         mode='lines',
    #         visible=True,
    #         showlegend=True,
    #         xhoverformat='%Y/%m/%d',
    #         yhoverformat='.2f'
    #     ), secondary_y=True
    # )
    #
    # fig.update_layout(
    #     # title=f'{self.tag} Trix',
    #     plot_bgcolor='white',
    #     xaxis_rangeslider=dict(visible=False),
    #     xaxis=dict(
    #         title='날짜',
    #         showticklabels=True,
    #         tickformat='%Y/%m/%d',
    #         zeroline=False,
    #         showgrid=True,
    #         gridcolor='lightgrey',
    #         autorange=True,
    #         showline=True,
    #         linewidth=1,
    #         linecolor='grey',
    #         mirror=False,
    #     ),
    #     yaxis=dict(
    #         showticklabels=True,
    #         zeroline=False,
    #         showgrid=True,
    #         gridcolor='lightgrey',
    #         autorange=True,
    #         showline=True,
    #         linewidth=0.5,
    #         linecolor='grey',
    #         mirror=False
    #     )
    # )
    #
    # # noinspection PyBroadException
    # try:
    #     desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    # except:
    #     desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    #
    # path = f'{desktop}/tdat/{datetime.now().strftime("%Y-%m-%d")}/MACRO'
    # if not os.path.isdir(path):
    #     os.makedirs(path)
    # of.plot(fig, filename=f'{path}/{save_filename}.html', auto_open=False)


