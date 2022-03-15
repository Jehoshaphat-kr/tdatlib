import requests, json
import pandas as pd
import numpy as np
from urllib.request import urlopen
from bs4 import BeautifulSoup as Soup


def getCorpSummary(ticker:str):
    """
    Fn Guide 기업 요약
    :param ticker: 종목코드
    """
    link = f"http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{ticker}&cID=&MenuYn=Y&ReportGB=D&NewMenuID=Y&stkGb=701"
    html = requests.get(link).content
    texts = Soup(html, 'lxml').find('ul', id='bizSummaryContent').find_all('li')
    text = '\n\n '.join([text.text for text in texts])

    syllables = []
    for n in range(1, len(text) - 2):
        if text[n] == '.':
            if text[n - 1].isdigit() or text[n + 1].isdigit() or text[n + 1].isalpha():
                syllables.append('.')
            else:
                syllables.append('.\n')
        else:
            syllables.append(text[n])
    return ' ' + text[0] + ''.join(syllables) + text[-2] + text[-1]

def getMainTables(ticker:str) -> list:
    """
    FnGuide SnapShot 페이지 HTML Table 발췌
    """
    head = f"http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{ticker}"
    tail = f"&cID=&MenuYn=Y&ReportGB=D&NewMenuID=Y&stkGb=701"
    return pd.read_html(head + tail, encoding='utf-8')

def getCorpTables(ticker:str) -> list:
    """
    FnGuide 기업개요 페이지 HTML Table 발췌
    """
    head = f"http://comp.fnguide.com/SVO2/ASP/SVD_Corp.asp?pGB=1&gicode=A{ticker}"
    tail = f"&cID=&MenuYn=Y&ReportGB=&NewMenuID=102&stkGb=701"
    return pd.read_html(head + tail, encoding='utf-8')

def getAnnualStatement(ticker:str, htmls=None) -> pd.DataFrame:
    """
    연간 기본 실적
                    매출액 영업이익  영업이익(발표기준)  당기순이익  ...    PER   PBR  발행주식수  배당수익률
    2016/12     2018667.0  292407.0            292407.0    227261.0  ...  13.18  1.48  7033967.0         1.58
    2017/12     2395754.0  536450.0            536450.0    421867.0  ...   9.40  1.76  6454925.0         1.67
    2018/12     2437714.0  588867.0            588867.0    443449.0  ...   6.42  1.10  5969783.0         3.66
    2019/12     2304009.0  277685.0            277685.0    217389.0  ...  17.63  1.49  5969783.0         2.54
    2020/12     2368070.0  359939.0            359939.0    264078.0  ...  21.09  2.06  5969783.0         3.70
    2021/12(P)  2790400.0  515700.0            515700.0         NaN  ...    NaN   NaN        NaN          NaN
    2022/12(E)  3017532.0  558278.0                 NaN    428421.0  ...  12.61  1.65        NaN          NaN
    2023/12(E)  3278481.0  662686.0                 NaN    511360.0  ...  10.56  1.49        NaN          NaN
    """
    if not isinstance(htmls, list) or not htmls:
        htmls = getMainTables(ticker=ticker)

    statement = htmls[14] if htmls[11].iloc[0].isnull().sum() > htmls[14].iloc[0].isnull().sum() else htmls[11]
    cols = statement.columns.tolist()
    statement.set_index(keys=[cols[0]], inplace=True)
    statement.index.name = None
    statement.columns = statement.columns.droplevel()
    return statement.T

def getQuarterStatement(ticker:str, htmls=None) -> pd.DataFrame:
    """
    분기 기본 실적
                   매출액  영업이익  영업이익(발표기준)  당기순이익  ...  PER   PBR  발행주식수  배당수익률
    2020/09      81288.0    13019.0             13019.0     10845.0  ...  NaN  1.15   728002.0          NaN
    2020/12      79662.0     9589.0              9589.0     17704.0  ...  NaN  1.59   728002.0         0.99
    2021/03      84942.0    13244.0             13244.0      9926.0  ...  NaN  1.76   728002.0          NaN
    2021/06     103217.0    26946.0             26946.0     19884.0  ...  NaN  1.62   728002.0          NaN
    2021/09     118053.0    41718.0             41718.0     33153.0  ...  NaN  1.23   728002.0          NaN
    2021/12(E)  123607.0    41844.0                 NaN     33903.0  ...  NaN   NaN        NaN          NaN
    2022/03(E)  112451.0    30024.0                 NaN     21875.0  ...  NaN   NaN        NaN          NaN
    2022/06(E)  115935.0    28307.0                 NaN     17382.0  ...  NaN   NaN        NaN          NaN
    """
    if not isinstance(htmls, list) or not htmls:
        htmls = getMainTables(ticker=ticker)

    statement = htmls[15] if htmls[11].iloc[0].isnull().sum() > htmls[14].iloc[0].isnull().sum() else htmls[12]
    cols = statement.columns.tolist()
    statement.set_index(keys=[cols[0]], inplace=True)
    statement.index.name = None
    statement.columns = statement.columns.droplevel()
    return statement.T

def getForeignRate(ticker:str) -> pd.DataFrame:
    """
    KRX 상장 기업 한정, 외국인 소진율
                           (Daily) 3M             (Weekly) 1Y            (Monthly) 3Y
                  종가 외국인보유비중     종가 외국인보유비중     종가 외국인보유비중
    날짜
    2019-01-01    NaN            NaN      NaN             NaN    42369          56.04
    2019-02-01    NaN            NaN      NaN             NaN    46309          56.72
    2019-03-01    NaN            NaN      NaN             NaN    44560          56.75
    ...           ...            ...      ...             ...      ...            ...
    2022-01-05  77400          51.99      NaN             NaN      NaN            NaN
    2022-01-06  76900          52.03      NaN             NaN      NaN            NaN
    2022-01-07  78300          52.11    77980           52.02      NaN            NaN
    """
    objs = dict()
    for dt in ['3M', '1Y', '3Y']:
        url = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_{dt}.json"
        data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
        frame = pd.DataFrame(data["CHART"])[['TRD_DT', 'J_PRC', 'FRG_RT']].rename(columns={
            'TRD_DT': '날짜', 'J_PRC': '종가', 'FRG_RT': '외국인보유비중'
        }).set_index(keys='날짜')
        frame.index = pd.to_datetime(frame.index)
        objs[dt] = frame
    return pd.concat(objs=objs, axis=1)

def getConsensus(ticker:str) -> pd.DataFrame:
    """
                투자의견  목표주가   종가
    날짜
    2021-03-15      3.96    104875  81800
    2021-03-16      3.96    104875  82800
    2021-03-17      3.96    105304  82300
    ...              ...       ...    ...
    2022-03-08      3.96     99208  69500
    2022-03-10      3.96     99208  71200
    2022-03-11      3.96     99208  70000
    """
    url = f"http://cdn.fnguide.com/SVO2/json/chart/01_02/chart_A{ticker}.json"
    data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
    consensus = pd.DataFrame(data['CHART']).rename(columns={
        'TRD_DT': '날짜', 'VAL1': '투자의견', 'VAL2': '목표주가', 'VAL3': '종가'
    }).set_index(keys='날짜')
    consensus.index = pd.to_datetime(consensus.index)
    consensus['목표주가'] = consensus['목표주가'].apply(lambda x: x if x else np.nan)
    return consensus

def getShorts(ticker:str) -> pd.DataFrame:
    """
               차입공매도비중  수정 종가
    날짜
    2021-01-11              0    133000
    2021-01-18              0    130000
    2021-01-25           0.03    135000
           ...            ...       ...
    2021-12-20           2.58    120500
    2021-12-27           1.18    126000
    2022-01-03           0.98    128500
    """
    url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{ticker}_SELL1Y.json"
    data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
    shorts = pd.DataFrame(data['CHART']).rename(columns={
        'TRD_DT': '날짜', 'VAL': '차입공매도비중', 'ADJ_PRC': '수정 종가'
    }).set_index(keys='날짜')
    shorts.index = pd.to_datetime(shorts.index)
    return shorts

def getShortBalance(ticker:str) -> pd.DataFrame:
    """
                대차잔고비중   수정 종가
    날짜
    2021-01-11          1.95      133000
    2021-01-18          2.07      130000
    2021-01-25          2.11      135000
           ...           ...         ...
    2021-12-20          2.71      120500
    2021-12-27          2.68      126000
    2022-01-03          2.36      128500
    """
    url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{ticker}_BALANCE1Y.json"
    data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
    balance = pd.DataFrame(data['CHART'])[['TRD_DT', 'BALANCE_RT', 'ADJ_PRC']].rename(columns={
        'TRD_DT': '날짜', 'BALANCE_RT': '대차잔고비중', 'ADJ_PRC': '수정 종가'
    }).set_index(keys='날짜')
    balance.index = pd.to_datetime(balance.index)
    return balance

def getMultiFactor(ticker:str) -> pd.DataFrame:
    """
                 SK하이닉스 반도체(업종)
    팩터
    베타               0.80         0.31
    배당성            -0.08        -1.03
    수익건전성         1.09        -0.12
    성장성             0.28        -0.05
    기업투자          -0.67        -0.14
    거시경제 민감도   -0.18        -0.32
    모멘텀            -0.34         0.20
    단기 Return        0.35         0.50
    기업규모           0.84        -2.36
    거래도            -0.14         0.68
    밸류               0.16        -0.36
    변동성            -0.24         0.64
    """
    url = f"http://cdn.fnguide.com/SVO2/json/chart/05_05/A{ticker}.json"
    data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(data['CHART_H'])['NAME'].tolist()
    factors = pd.DataFrame(data['CHART_D']).rename(
        columns=dict(zip(['NM', 'VAL1', 'VAL2'], ['팩터'] + header))
    ).set_index(keys='팩터')
    return factors

def getRelReturnsBMark(ticker:str) -> pd.DataFrame:
    """
                                          (Daily) 3M                          (Weekly) 1Y
                SK하이닉스  코스피 전기,전자   KOSPI  SK하이닉스  코스피 전기,전자  KOSPI
    TRD_DT
    2021-01-15         NaN              NaN      NaN      100.00           100.00  100.00
    2021-01-22         NaN              NaN      NaN       99.69            98.44   99.13
    2021-01-29         NaN              NaN      NaN       97.70            97.66   99.10
    ...                ...              ...      ...         ...              ...     ...
    2022-01-05      137.16           113.68   101.29         NaN              NaN     NaN
    2022-01-06      136.61           112.58   100.14         NaN              NaN     NaN
    2022-01-07      138.80           114.45   101.32       97.17            90.77   94.56
    """
    objs = {}
    for period in ['3M', '1Y']:
        url = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_{period}.json"
        data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
        header = pd.DataFrame(data["CHART_H"])[['ID', 'PREF_NAME']]
        header = header[header['PREF_NAME'] != ""]
        inner = pd.DataFrame(data["CHART"])[
            ['TRD_DT'] + header['ID'].tolist()
        ].set_index(keys='TRD_DT').rename(columns=header.set_index(keys='ID').to_dict()['PREF_NAME'])
        inner.index = pd.to_datetime(inner.index)
        objs[period] = inner
    return pd.concat(objs=objs, axis=1)

def getRelMultiples(ticker:str) -> pd.DataFrame:
    """
                                           PER                               EV/EBITA                                    ROE
          SK하이닉스  코스피 전기,전자  코스피   SK하이닉스  코스피 전기,전자  코스피   SK하이닉스  코스피 전기,전자  코스피
    2019       34.15            21.90    20.01         6.76              6.85    7.21         4.23              6.11    4.69
    2020       18.14            19.87    22.35         6.37              8.06    8.57         9.53              9.26    5.26
    2021E       9.72            13.28    11.10         4.27              4.65    6.44        16.86             14.15   11.62
    """
    url = f"http://cdn.fnguide.com/SVO2/json/chart/01_04/chart_A{ticker}_D.json"
    data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
    objs = {}
    for label, index in (('PER', '02'), ('EV/EBITA', '03'), ('ROE', '04')):
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

def getProducts(ticker:str) -> pd.DataFrame:
    """
                IM  반도체     CE     DP  기타(계)
    기말
    2017/12  44.42   30.92  18.79  14.35     -8.48
    2018/12  41.30   35.40  17.30  13.30     -7.30
    2019/12  46.56   28.19  19.43  13.48     -7.65
    2020/12  42.05   30.77  20.34  12.92     -6.08
    """
    url = f"http://cdn.fnguide.com/SVO2//json/chart/02/chart_A{ticker}_01_N.json"
    src = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(src['chart_H'])[['ID', 'NAME']].set_index(keys='ID')
    header = header.to_dict()['NAME']
    header.update({'PRODUCT_DATE':'기말'})
    return pd.DataFrame(src['chart']).rename(columns=header).set_index(keys='기말')

def getProductsPie(ticker:str, products=None) -> pd.Series:
    """
    IM        42.05
    반도체    30.77
    CE        20.34
    DP         6.84
    """
    if not isinstance(products, pd.DataFrame) or not products:
        products = getProducts(ticker=ticker)
    df = products.iloc[-1].T.dropna().astype(float)
    df.drop(index=df[df < 0].index, inplace=True)
    df[df.index[-1]] += (100 - df.sum())
    df.name = '비중'
    return df

def getCosts(ticker:str, htmls=None) -> pd.DataFrame:
    """
            판관비율  매출원가율  R&D투자비중  무형자산처리비중  당기비용처리비중
    2016/12      NaN         NaN         7.33             0.34               6.99
    2017/12    23.64       53.97         7.01             0.19               6.83
    2018/12    21.53       54.31         7.65             0.12               7.53
    2019/12    24.04       63.91         8.77             0.12               8.65
    2020/12    23.79       61.02         8.96             0.05               8.92
    """
    if not isinstance(htmls, list) or not htmls:
        htmls = getCorpTables(ticker=ticker)

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
    return pd.concat(objs=[sales_cost.T, sg_n_a.T, r_n_d], axis=1).sort_index(ascending=True)

if __name__ == '__main__':
    pd.set_option('display.expand_frame_repr', False)

    _ticker = '005930'
    # print(getCorpSummary(ticker=_ticker))
    # print(getForeignRate(ticker=_ticker))
    # print(getConsensus(ticker=_ticker))
    # print(getShorts(ticker=_ticker))
    # print(getShortBalance(ticker=_ticker))
    # print(getMultiFactor(ticker=_ticker))
    # print(getRelativeReturns(ticker=_ticker))
    # print(getRelativeMultiples(ticker=_ticker))
    # print(getProducts(ticker=_ticker))
    # print(getAnnualStatement(ticker=_ticker))
    # print(getQuarterStatement(ticker=_ticker))
    print(getCosts(ticker=_ticker))