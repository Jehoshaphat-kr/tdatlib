from pandas_datareader import get_data_fred as fred
from datetime import datetime, timedelta
from xml.etree.ElementTree import ElementTree, fromstring
import pandas as pd
import requests


KEY = "CEW3KQU603E6GA8VX0O9"


def fetch_fred(symbols:str or list, period:int = 10):
    today = datetime.now().date()
    start = today - timedelta(period * 365)
    end = today
    return fred(symbols=symbols, start=start, end=end)


class fetch_ecos(object):

    _exclude = ['row', 'P_STAT_CODE']
    def __init__(self):
        return

    def _xml_to_df(self, url:str) -> pd.DataFrame:
        resp = requests.get(url)
        root = ElementTree(fromstring(resp.text)).getroot()

        data = list()
        for tag in root.findall('row'):
            getter = dict()
            for n, t in enumerate([inner for inner in tag.iter()]):
                if t.tag in self._exclude:
                    continue
                getter.update({t.tag: t.text})
            data.append(getter)

        return pd.DataFrame(data=data) if data else pd.DataFrame()

    @property
    def codes(self) -> pd.DataFrame:
        if not hasattr(self, '__codes'):
            url = f"http://ecos.bok.or.kr/api/StatisticTableList/{KEY}/xml/kr/1/10000/"
            df = self._xml_to_df(url=url)
            df = df[df.SRCH_YN == 'Y'].copy()
            df['STAT_NAME'] = df.STAT_NAME.apply(lambda x: x[x.find(' ') + 1:])
            df = df.drop(columns='SRCH_YN')
            df = df.rename(columns={'STAT_CODE':'코드', 'STAT_NAME':'지표명', 'CYCLE':'주기', 'ORG_NAME':'발행처'})
            self.__setattr__('__codes', df)
        return self.__getattribute__('__codes')

    def fetch(self, codes:list or str, start_year:str='2015', end_year:str='2022'):
        if type(codes) == str:
            codes = [codes]

        yy = start_year
        ee = end_year
        samples = self.codes[self.codes.코드.isin(codes)]
        for code, label, cyc in zip(samples.코드, samples.지표명, samples.주기):
            s = f'{yy}0101' if cyc == 'D' else f'{yy}01S1' if cyc == 'SM' else f'{yy}01' if cyc == 'M' else f'{yy}{cyc}1'
            e = f'{ee}1230' if cyc == 'D' else f'{ee}12S1' if cyc == 'SM' else f'{ee}12' if cyc == 'M' else f'{ee}{cyc}12'
            suffix = s[-4:] if len(s) == 8 else s[-2:]
            url = f'http://ecos.bok.or.kr/api/StatisticSearch/{KEY}/xml/kr/1/100000/{code}/{cyc}/{s}/{e}'
            df = self._xml_to_df(url=url)
            df.to_csv(rf'./{code}_{label}.csv', index=False, encoding='euc-kr')



def fetch_kr():
    url = "http://ecos.bok.or.kr/api/KeyStatisticList/XT2S2EESV0C0728KFJBT/json/kr/1/100/"
    resp = requests.get(url)
    data = resp.json()
    return data


if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)
    # data = fetch_kr()
    # frm = pd.DataFrame(data['KeyStatisticList']['row'])
    # file = open('./raw.txt', 'w')
    # file.write(str(data))
    # file.close()
    # print(frm)
    # frm.to_csv('./test.csv', encoding='euc-kr', index=False)

    ecos = fetch_ecos()
    # print(ecos.codes)
    # ecos.codes.to_csv(r'./test.csv', encoding='euc-kr')

    ecos.fetch(
        codes=[
            '802Y001',
            '901Y013',
            '301Y017',
            '731Y003',
            '511Y003'
        ]
    )


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


