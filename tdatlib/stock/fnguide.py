from datetime import datetime, timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup as Soup
from pykrx import stock
from inspect import currentframe as inner
import requests, json
import pandas as pd
import numpy as np


def getSummary(ticker:str) -> str:
    url = f"http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{ticker}&cID=&MenuYn=Y&ReportGB=D&NewMenuID=Y&stkGb=701"
    texts = Soup(requests.get(url).content, 'lxml').find('ul', id='bizSummaryContent').find_all('li')
    text = '\n\n '.join([text.text for text in texts])
    words = []
    for n in range(1, len(text) - 2):
        if text[n] == '.':
            words.append('.' if text[n - 1].isdigit() or text[n + 1].isdigit() or text[n + 1].isalpha() else '.\n')
        else:
            words.append(text[n])
    return ' ' + text[0] + ''.join(words) + text[-2] + text[-1]


def getAllProducts(ticker: str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2//json/chart/02/chart_A{ticker}_01_N.json"
    src = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(src['chart_H'])[['ID', 'NAME']].set_index(keys='ID').to_dict()['NAME']
    header.update({'PRODUCT_DATE': '기말'})
    products = pd.DataFrame(src['chart']).rename(columns=header).set_index(keys='기말')

    i = products.columns[-1]
    products['Sum'] = products.astype(float).sum(axis=1)
    products = products[(90 <= products.Sum) & (products.Sum < 110)].astype(float)
    products[i] = products[i] - (products.Sum - 100)
    return products.drop(columns=['Sum'])


def getRecentProducts(ticker: str = str(), products: pd.DataFrame = None) -> pd.DataFrame:
    if not isinstance(products, pd.DataFrame):
        products = getAllProducts(ticker=ticker)
    i = -1 if products.iloc[-1].astype(float).sum() > 10 else -2
    df = products.iloc[i].T.dropna().astype(float)
    df.drop(index=df[df < 0].index, inplace=True)
    df[df.index[i]] += (100 - df.sum())
    return df[df.values != 0]


def getStatement(ticker:str, **kwargs) -> pd.DataFrame:
    url = f"http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{ticker}&cID=&MenuYn=Y&ReportGB=D&NewMenuID=Y&stkGb=701"
    html = kwargs['html'] if 'html' in kwargs.keys() else pd.read_html(url, header=0)
    kind = kwargs['kind'] if 'kind' in kwargs.keys() else 'annual'
    if kind == 'annual':
        statement = html[14] if html[11].iloc[0].isnull().sum() > html[14].iloc[0].isnull().sum() else html[11]
    elif kind == 'quarter':
        statement = html[15] if html[11].iloc[0].isnull().sum() > html[14].iloc[0].isnull().sum() else html[12]
    else:
        raise KeyError

    cols = statement.columns.tolist()
    statement.set_index(keys=[cols[0]], inplace=True)
    statement.index.name = None
    if isinstance(statement.columns[0], tuple):
        statement.columns = statement.columns.droplevel()
    else:
        statement.columns = statement.iloc[0]
        statement.drop(index=statement.index[0], inplace=True)
    return statement.T


def getExpenses(ticker:str) -> pd.DataFrame:
    url = f"http://comp.fnguide.com/SVO2/ASP/SVD_Corp.asp?pGB=1&gicode=A{ticker}&cID=&MenuYn=Y&ReportGB=&NewMenuID=102&stkGb=701"
    html = pd.read_html(url, header=0)

    sales_cost = html[4].set_index(keys=['항목'])
    sales_cost.index.name = None

    sg_n_a = html[5].set_index(keys=['항목'])
    sg_n_a.index.name = None

    r_n_d = html[8].set_index(keys=['회계연도'])
    r_n_d.index.name = None
    r_n_d = r_n_d[['R&D 투자 총액 / 매출액 비중.1', '무형자산 처리 / 매출액 비중.1', '당기비용 처리 / 매출액 비중.1']]
    r_n_d = r_n_d.rename(columns={
        'R&D 투자 총액 / 매출액 비중.1': 'R&D투자비중',
        '무형자산 처리 / 매출액 비중.1': '무형자산처리비중',
        '당기비용 처리 / 매출액 비중.1': '당기비용처리비중'
    })
    if '관련 데이터가 없습니다.' in r_n_d.index:
        r_n_d.drop(index=['관련 데이터가 없습니다.'], inplace=True)
    return pd.concat(objs=[sales_cost.T, sg_n_a.T, r_n_d], axis=1).sort_index(ascending=True).astype(float)


def getConsensus(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/01_02/chart_A{ticker}.json"
    raw = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    frm = pd.DataFrame(raw['CHART'])
    frm = frm.rename(columns={'TRD_DT': '날짜', 'VAL1': '투자의견', 'VAL2': '목표주가', 'VAL3': '종가'})
    frm = frm.set_index(keys='날짜')
    frm.index = pd.to_datetime(frm.index)
    frm['목표주가'] = frm['목표주가'].apply(lambda x: int(x) if x else np.nan)
    frm['종가'] = frm['종가'].astype(int)
    return frm


def getForeigner(ticker:str) -> pd.DataFrame:
    objs = dict()
    for dt in ['3M', '1Y', '3Y']:
        url = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_{dt}.json"
        data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
        frm = pd.DataFrame(data["CHART"])[['TRD_DT', 'J_PRC', 'FRG_RT']]
        frm = frm.rename(columns={'TRD_DT':'날짜', 'J_PRC':'종가', 'FRG_RT':'외국인보유비중'}).set_index(keys='날짜')
        frm.index = pd.to_datetime(frm.index)
        frm = frm.replace('', '0.0')
        frm['종가'] = frm['종가'].astype(int)
        frm['외국인보유비중'] = frm['외국인보유비중'].astype(float)
        objs[dt] = frm
    return pd.concat(objs=objs, axis=1)


def getNps(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/05/chart_A{ticker}_D.json"
    src = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(src['01_Y_H'])[['ID', 'NAME']].set_index(keys='ID').to_dict()['NAME']
    header.update({'GS_YM': '날짜'})
    data = pd.DataFrame(src['01_Y']).rename(columns=header)[header.values()].set_index(keys='날짜')
    data = data[data != '-']
    for col in data.columns:
        data[col] = data[col].astype(str).str.replace(',', '').astype(float)

    missing = [col for col in ['EPS', 'BPS', 'EBITDAPS', '보통주DPS'] if not col in data.columns]
    if missing:
        data[missing] = np.nan
    return data


def getMultifactor(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/05_05/A{ticker}.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(data['CHART_H'])['NAME'].tolist()
    return pd.DataFrame(data['CHART_D']).rename(
        columns=dict(zip(['NM', 'VAL1', 'VAL2'], ['팩터'] + header))
    ).set_index(keys='팩터').astype(float)


def getBenchmarkReturn(ticker:str):
    objs = dict()
    for period in ['3M', '1Y']:
        url = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_{period}.json"
        data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
        header = pd.DataFrame(data["CHART_H"])[['ID', 'PREF_NAME']]
        header = header[header['PREF_NAME'] != ""]
        inner = pd.DataFrame(data["CHART"])[
            ['TRD_DT'] + header['ID'].tolist()
            ].set_index(keys='TRD_DT').rename(columns=header.set_index(keys='ID').to_dict()['PREF_NAME'])
        inner.index = pd.to_datetime(inner.index)
        objs[period] = inner
    return pd.concat(objs=objs, axis=1)


def getBenchmarkMultiple(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/01_04/chart_A{ticker}_D.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    objs = dict()
    for label, index in (('PER', '02'), ('EV/EBITDA', '03'), ('ROE', '04')):
        header1 = pd.DataFrame(data[f'{index}_H'])[['ID', 'NAME']].set_index(keys='ID')
        header1['NAME'] = header1['NAME'].astype(str).str.replace("'", "20")
        header1 = header1.to_dict()['NAME']
        header1.update({'CD_NM': '이름'})

        inner1 = pd.DataFrame(data[index])[list(header1.keys())].rename(columns=header1).set_index(keys='이름')
        inner1.index.name = None
        for col in inner1.columns:
            inner1[col] = inner1[col].apply(lambda x: np.nan if x == '-' else x)
        objs[label] = inner1.T
    return pd.concat(objs=objs, axis=1)


def getShortSell(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{ticker}_SELL1Y.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    frm = pd.DataFrame(data['CHART'])
    frm = frm.rename(columns={'TRD_DT': '날짜', 'VAL': '차입공매도비중', 'ADJ_PRC': '수정종가'}).set_index(keys='날짜')
    frm.index = pd.to_datetime(frm.index)
    frm['수정종가'] = frm['수정종가'].astype(int)
    frm['차입공매도비중'] = frm['차입공매도비중'].astype(float)
    return frm


def getShortBalance(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{ticker}_BALANCE1Y.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    frm = pd.DataFrame(data['CHART'])[['TRD_DT', 'BALANCE_RT', 'ADJ_PRC']]
    frm = frm.rename(columns={'TRD_DT': '날짜', 'BALANCE_RT': '대차잔고비중', 'ADJ_PRC': '수정종가'}).set_index(keys='날짜')
    frm.index = pd.to_datetime(frm.index)
    frm['수정종가'] = frm['수정종가'].astype(int)
    frm['대차잔고비중'] = frm['대차잔고비중'].astype(float)
    return frm


def getMultipleBand(ticker:str) -> (pd.DataFrame, pd.DataFrame):
    url = f"http://cdn.fnguide.com/SVO2/json/chart/01_06/chart_A{ticker}_D.json"
    src = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    per_header = pd.DataFrame(src['CHART_E'])[['ID', 'NAME']].set_index(keys='ID')
    pbr_header = pd.DataFrame(src['CHART_B'])[['ID', 'NAME']].set_index(keys='ID')
    per_header, pbr_header = per_header.to_dict()['NAME'], pbr_header.to_dict()['NAME']
    per_header.update({'GS_YM': '날짜'})
    pbr_header.update({'GS_YM': '날짜'})

    df = pd.DataFrame(src['CHART'])
    per = df[per_header.keys()].replace('-', np.NaN).replace('', np.NaN)
    pbr = df[pbr_header.keys()].replace('-', np.NaN).replace('', np.NaN)
    per['GS_YM'], pbr['GS_YM'] = pd.to_datetime(per['GS_YM']), pd.to_datetime(pbr['GS_YM'])
    return per.rename(columns=per_header).set_index(keys='날짜'), pbr.rename(columns=pbr_header).set_index(keys='날짜')


def getMultipleSeries(ticker:str) -> pd.DataFrame:
    todate = datetime.today().strftime("%Y%m%d")
    fromdate = (datetime.today() - timedelta(3 * 365)).strftime("%Y%m%d")
    return stock.get_market_fundamental(fromdate, todate, ticker)


class _fnguide(object):

    __by = 'annual'
    def __init__(self, ticker:str):
        self._t = ticker
        return

    def __property__(self, key, **kwargs):
        if not hasattr(self, f'_{self._t}_{key}'):
            fname = f'get{key}' if not key.startswith('Statement') else f'getStatement'
            self.__setattr__(f'_{self._t}_{key}', globals()[fname](self._t, **kwargs))
        return self.__getattribute__(f'_{self._t}_{key}')

    @property
    def by(self) -> str:
        return self.__by

    @by.setter
    def by(self, period:str):
        if not period in ['annual', 'quarter']:
            raise KeyError
        self.__by = period

    @property
    def Summary(self) -> str:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def AllProducts(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def RecentProducts(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name, products=self.AllProducts)

    @property
    def Statement(self) -> pd.DataFrame:
        return self.__property__(key=f'{inner().f_code.co_name}_{self.by}', kind=self.by)

    @property
    def Asset(self) -> pd.DataFrame:
        asset = self.Statement[['자산총계', '부채총계', '자본총계']].dropna().astype(int).copy()
        for col in asset.columns:
            asset[f'{col}LB'] = asset[col].apply(lambda x: f'{x}억원' if x < 10000 else f'{str(x)[:-4]}조 {str(x)[-4:]}억원')
        return asset

    @property
    def Profit(self) -> pd.DataFrame:
        key = [_ for _ in ['매출액', '순영업수익', '이자수익', '보험료수익'] if _ in self.Statement.columns][0]
        profit = self.Statement[[key, '영업이익', '당기순이익']].dropna().astype(int)
        for col in [key, '영업이익', '당기순이익']:
            profit[f'{col}LB'] = profit[col].apply(lambda x: f'{x}억원' if x < 10000 else f'{str(x)[:-4]}조 {str(x)[-4:]}억원')
        return profit

    @property
    def Expenses(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def Foreigner(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def Consensus(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def Nps(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def BenchmarkReturn(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def BenchmarkMultiple(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def Multifactor(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def MultipleSeries(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def MultipleBand(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def ShortSell(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)

    @property
    def ShortBalance(self) -> pd.DataFrame:
        return self.__property__(key=inner().f_code.co_name)


if __name__ == '__main__':
    ticker = '316140'
    tester = _fnguide(ticker=ticker)
    # print(tester.Summary)
    print(tester.AllProducts)
    print(tester.RecentProducts)
    # print(tester.Statement)
    # print(tester.Asset)
    # print(tester.Profit)
    # print(tester.Expenses)
    # print(tester.Foreigner)
    # print(tester.Consensus)
    # print(tester.Nps)
    # print(tester.BenchmarkReturn)
    # print(tester.BenchmarkMultiple)
    # print(tester.Multifactor)
    # print(tester.MultipleSeries)
    # print(tester.MultipleBand)
    # print(tester.ShortSell)
    # print(tester.ShortBalance)
