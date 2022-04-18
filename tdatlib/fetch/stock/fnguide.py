import requests, json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup as Soup
from pykrx import stock


URL1 = "http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A%s&cID=&MenuYn=Y&ReportGB=D&NewMenuID=Y&stkGb=701"
URL2 = "http://comp.fnguide.com/SVO2/ASP/SVD_Corp.asp?pGB=1&gicode=A%s&cID=&MenuYn=Y&ReportGB=&NewMenuID=102&stkGb=701"
URL_PRODUCTS  = "http://cdn.fnguide.com/SVO2//json/chart/02/chart_A%s_01_N.json"
URL_FACTORS   = "http://cdn.fnguide.com/SVO2/json/chart/05_05/A%s.json"
URL_RETURNS   = "http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A%s_%s.json"
URL_MULTIPLE  = "http://cdn.fnguide.com/SVO2/json/chart/01_04/chart_A%s_D.json"
URL_CONSENSUS = "http://cdn.fnguide.com/SVO2/json/chart/01_02/chart_A%s.json"
URL_FOREIGNER = "http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A%s_%s.json"
URL_SHORTSELL = "http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A%s_SELL1Y.json"
URL_BALANCE   = "http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A%s_BALANCE1Y.json"
URL_MULTIBAND = "http://cdn.fnguide.com/SVO2/json/chart/01_06/chart_A%s_D.json"
URL_NPS       = "http://cdn.fnguide.com/SVO2/json/chart/05/chart_A%s_D.json"


def fetch_summary(ticker:str) -> str:
    texts = Soup(requests.get(URL1 % ticker).content, 'lxml').find('ul', id='bizSummaryContent').find_all('li')
    text = '\n\n '.join([text.text for text in texts])
    words = []
    for n in range(1, len(text) - 2):
        if text[n] == '.':
            words.append('.' if text[n - 1].isdigit() or text[n + 1].isdigit() or text[n + 1].isalpha() else '.\n')
        else:
            words.append(text[n])
    return ' ' + text[0] + ''.join(words) + text[-2] + text[-1]


def fetch_products(ticker:str) -> pd.DataFrame:
    src = json.loads(urlopen(URL_PRODUCTS % ticker).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(src['chart_H'])[['ID', 'NAME']].set_index(keys='ID').to_dict()['NAME']
    header.update({'PRODUCT_DATE': '기말'})
    products = pd.DataFrame(src['chart']).rename(columns=header).set_index(keys='기말')

    i = -1 if products.iloc[-1].astype(float).sum() > 10 else -2
    df = products.iloc[i].T.dropna().astype(float)
    df.drop(index=df[df < 0].index, inplace=True)
    df[df.index[i]] += (100 - df.sum())
    return df[df.values != 0]


def fetch_statement(htmls:list, kind:str) -> pd.DataFrame:
    if kind == 'annual':
        statement = htmls[14] if htmls[11].iloc[0].isnull().sum() > htmls[14].iloc[0].isnull().sum() else htmls[11]
    elif kind == 'quarter':
        statement = htmls[15] if htmls[11].iloc[0].isnull().sum() > htmls[14].iloc[0].isnull().sum() else htmls[12]
    else:
        raise KeyError

    cols = statement.columns.tolist()
    statement.set_index(keys=[cols[0]], inplace=True)
    statement.index.name = None
    statement.columns = statement.columns.droplevel()
    return statement.T


def fetch_multifactor(ticker:str) -> pd.DataFrame:
    data = json.loads(urlopen(URL_FACTORS % ticker).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(data['CHART_H'])['NAME'].tolist()
    return pd.DataFrame(data['CHART_D']).rename(
        columns=dict(zip(['NM', 'VAL1', 'VAL2'], ['팩터'] + header))
    ).set_index(keys='팩터').astype(float)


def fetch_benchmark_return(ticker:str):
    objs = {}
    for period in ['3M', '1Y']:
        data = json.loads(urlopen(URL_RETURNS % (ticker, period)).read().decode('utf-8-sig', 'replace'))
        header = pd.DataFrame(data["CHART_H"])[['ID', 'PREF_NAME']]
        header = header[header['PREF_NAME'] != ""]
        inner = pd.DataFrame(data["CHART"])[
            ['TRD_DT'] + header['ID'].tolist()
            ].set_index(keys='TRD_DT').rename(columns=header.set_index(keys='ID').to_dict()['PREF_NAME'])
        inner.index = pd.to_datetime(inner.index)
        objs[period] = inner
    return pd.concat(objs=objs, axis=1)


def fetch_benchmark_multiple(ticker:str) -> pd.DataFrame:
    data = json.loads(urlopen(URL_MULTIPLE % ticker).read().decode('utf-8-sig', 'replace'))
    objs = {}
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


def fetch_consensus(ticker:str) -> pd.DataFrame:
    data = json.loads(urlopen(URL_CONSENSUS % ticker).read().decode('utf-8-sig', 'replace'))
    consensus = pd.DataFrame(data['CHART']).rename(columns={
        'TRD_DT': '날짜', 'VAL1': '투자의견', 'VAL2': '목표주가', 'VAL3': '종가'
    }).set_index(keys='날짜')
    consensus.index = pd.to_datetime(consensus.index)
    consensus['목표주가'] = consensus['목표주가'].apply(lambda x: int(x) if x else np.nan)
    consensus['종가'] = consensus['종가'].astype(int)
    return consensus


def fetch_foreign_rate(ticker:str) -> pd.DataFrame:
    objs = dict()
    for dt in ['3M', '1Y', '3Y']:
        data = json.loads(urlopen(URL_FOREIGNER % (ticker, dt)).read().decode('utf-8-sig', 'replace'))
        frame = pd.DataFrame(data["CHART"])[['TRD_DT', 'J_PRC', 'FRG_RT']].rename(columns={
            'TRD_DT': '날짜', 'J_PRC': '종가', 'FRG_RT': '외국인보유비중'
        }).set_index(keys='날짜')
        frame.index = pd.to_datetime(frame.index)
        frame['종가'] = frame['종가'].astype(int)
        frame['외국인보유비중'] = frame['외국인보유비중'].astype(float)
        objs[dt] = frame
    return pd.concat(objs=objs, axis=1)


def fetch_short_sell(ticker:str) -> pd.DataFrame:
    data = json.loads(urlopen(URL_SHORTSELL % ticker).read().decode('utf-8-sig', 'replace'))
    shorts = pd.DataFrame(data['CHART']).rename(columns={
        'TRD_DT': '날짜', 'VAL': '차입공매도비중', 'ADJ_PRC': '수정종가'
    }).set_index(keys='날짜')
    shorts.index = pd.to_datetime(shorts.index)
    shorts['수정종가'] = shorts['수정종가'].astype(int)
    shorts['차입공매도비중'] = shorts['차입공매도비중'].astype(float)
    return shorts


def fetch_short_balance(ticker:str) -> pd.DataFrame:
    data = json.loads(urlopen(URL_BALANCE % ticker).read().decode('utf-8-sig', 'replace'))
    balance = pd.DataFrame(data['CHART'])[['TRD_DT', 'BALANCE_RT', 'ADJ_PRC']].rename(columns={
        'TRD_DT': '날짜', 'BALANCE_RT': '대차잔고비중', 'ADJ_PRC': '수정종가'
    }).set_index(keys='날짜')
    balance.index = pd.to_datetime(balance.index)
    balance['수정종가'] = balance['수정종가'].astype(int)
    balance['대차잔고비중'] = balance['대차잔고비중'].astype(float)
    return balance


def fetch_expenses(htmls:list) -> pd.DataFrame:
    sales_cost = htmls[4].set_index(keys=['항목'])
    sales_cost.index.name = None

    sg_n_a = htmls[5].set_index(keys=['항목'])
    sg_n_a.index.name = None

    r_n_d = htmls[8].set_index(keys=['회계연도'])
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


def fetch_multiple_band(ticker:str) -> (pd.DataFrame, pd.DataFrame):
    src = json.loads(urlopen(URL_MULTIBAND % ticker).read().decode('utf-8-sig', 'replace'))
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


def fetch_multiple_series(ticker:str) -> pd.DataFrame:
    todate = datetime.today().strftime("%Y%m%d")
    fromdate = (datetime.today() - timedelta(3 * 365)).strftime("%Y%m%d")
    return stock.get_market_fundamental(fromdate, todate, ticker)


def fetch_nps(ticker:str) -> pd.DataFrame:
    src = json.loads(urlopen(URL_NPS % ticker).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(src['01_Y_H'])[['ID', 'NAME']].set_index(keys='ID').to_dict()['NAME']
    header.update({'GS_YM': '날짜'})
    data = pd.DataFrame(src['01_Y']).rename(columns=header)[header.values()].set_index(keys='날짜')
    data = data[data != '-']
    for col in data.columns:
        data[col] = data[col].astype(str).str.replace(',', '').astype(float)
    return data
