import pandas as pd
import requests, time, json, os
import urllib.request as req
from tdatlib import archive
from tqdm import tqdm
from pytz import timezone
from datetime import datetime, timedelta
from pykrx import stock as krx


kst = datetime.now(timezone('Asia/Seoul'))
tdt = krx.get_nearest_business_day_in_a_week(date=kst.strftime("%Y%m%d"))
def getWiseDate() -> str:
    """
    WISE INDEX 산업 분류 기준 날짜
    :return: %Y%m%d
    """
    source = requests.get(url='http://www.wiseindex.com/Index/Index#/G1010.0.Components').text
    tic = source.find("기준일")
    toc = source[tic:].find("</p>")
    return source[tic + 6: tic + toc].replace('.', '')

def getWiseGroup(name:str, date:str=str()) -> pd.DataFrame:
    """"
    WISE INDEX 산업 분류
    :param name: WICS/WI26
    :param date: WISE 기준 날짜
    :return: 
    """
    if not name.lower() in ['wics', 'wi26']:
        raise KeyError(f'Argument Error: {name} - WICS/WI26 Only')
    if not date:
        date = getWiseDate()

    codes = archive.wics_code if name.lower() == 'wics' else archive.wi26_code
    frame = pd.DataFrame()
    for code, c_name in tqdm(codes.items(), desc=f'Fetch {name}'):
        url = f'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={date}&sec_cd={code}'
        while True:
            # noinspection PyBroadException
            try:
                load = requests.get(url).json()
                data = [[_['CMP_CD'], _['CMP_KOR'], _['SEC_NM_KOR'], _['IDX_NM_KOR'][5:]] for _ in load['list']]
                break
            except:
                print(f'\t- Parse error while fetching WISE INDEX {code} {c_name}')
                time.sleep(1)
        frame = pd.concat(
            objs=[frame, pd.DataFrame(data=data, columns=['종목코드', '종목명', '산업', '섹터'])],
            axis=0, ignore_index=True
        )
    frame['날짜'] = date
    if name.upper() == 'WI26':
        frame.drop(columns=['산업'], inplace=True)
    return frame.set_index(keys='종목코드')

def getCorpIPO() -> pd.DataFrame:
    """
                      종목명        IPO
    종목코드
    000210                DL 1976-02-02
    004840           DRB동일 1976-05-21
    155660               DSR 2013-05-15
    ...                  ...        ...
    222670  플럼라인생명과학 2015-07-28
    331660  한국미라클피플사 2019-10-28
    212310            휴벡셀 2016-07-26
    """
    link = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    ipo = pd.read_html(io=link, header=0)[0][['회사명', '종목코드', '상장일']]
    ipo = ipo.rename(columns={'회사명': '종목명', '상장일': 'IPO'}).set_index(keys='종목코드')
    ipo.index = ipo.index.astype(str).str.zfill(6)
    ipo.IPO = pd.to_datetime(ipo.IPO)
    return ipo

def getThemeGroup() -> pd.DataFrame:
    """
                 종목명          섹터
    종목코드
    211270       AP위성      우주항공
    138930  BNK금융지주          배당
    079160       CJ CGV  미디어컨텐츠
    ...             ...           ...
    298000     효성화학        수소차
    093370         후성       2차전지
    145020         휴젤        바이오
    """
    df = pd.read_csv(archive.theme, index_col='종목코드')
    df.index = df.index.astype(str).str.zfill(6)
    return df

def getEtfGroup() -> pd.DataFrame:
    """
                                      종목명          산업   섹터
    종목코드
    069500                         KODEX 200  국내 시장지수  대형
    278540               KODEX MSCI Korea TR  국내 시장지수  대형
    278530                       KODEX 200TR  국내 시장지수  대형
    ...                                  ...            ...   ...
    396520         TIGER 차이나반도체FACTSET           해외  중국
    391600    KINDEX 미국친환경그린테마INDXX           해외  미국
    391590         KINDEX 미국스팩&IPO INDXX           해외  미국
    """
    df = pd.read_csv(archive.etf, index_col='종목코드')
    df.index = df.index.astype(str).str.zfill(6)
    return df

def getEtfList() -> pd.DataFrame:
    """
                                 종목명   종가       시가총액
    종목코드
    069500                    KODEX 200  39725  5718400000000
    371460  TIGER 차이나전기차SOLACTIVE  16435  3229800000000
    278540          KODEX MSCI Korea TR  12820  2239700000000
    ...                             ...    ...            ...
    334700   KBSTAR 팔라듐선물인버스(H)   5520     1700000000
    287310         KBSTAR 200경기소비재  10895     1500000000
    287320             KBSTAR 200산업재  11135     1300000000
    """
    url = 'https://finance.naver.com/api/sise/etfItemList.nhn'
    key_prev, key_curr = ['itemcode', 'itemname', 'nowVal', 'marketSum'], ['종목코드', '종목명', '종가', '시가총액']
    df = pd.DataFrame(json.loads(req.urlopen(url).read().decode('cp949'))['result']['etfItemList'])
    df = df[key_prev].rename(columns=dict(zip(key_prev, key_curr)))
    df['시가총액'] = df['시가총액'] * 100000000
    return df.set_index(keys='종목코드')

def convertEtfExcel2Csv():
    """
    수기 관리 ETF 분류 Excel -> CSV변환
    """
    df = pd.read_excel(archive.etf_xl, index_col='종목코드')
    df.index = df.index.astype(str).str.zfill(6)
    df.to_csv(archive.etf, index=True, encoding='utf-8')
    return

def checkEtfLatest(etfs=None) -> bool:
    """
    로컬 수기 관리용 ETF 분류 최신화 현황 여부
    :param etfs: online ETF 리스트
    """
    curr = etfs if isinstance(etfs, pd.DataFrame) else getEtfList()
    prev = pd.read_excel(archive.etf_xl, index_col='종목코드')
    prev.index = prev.index.astype(str).str.zfill(6)
    to_be_delete = prev[~prev.index.isin(curr.index)]
    to_be_update = curr[~curr.index.isin(prev.index)]
    if to_be_delete.empty and to_be_update.empty:
        return True
    else:
        for kind, frm in [('삭제', to_be_delete), ('추가', to_be_update)]:
            if not frm.empty:
                print("-" * 70, f"\n▷ ETF 분류 {kind} 필요 항목: {'없음' if frm.empty else '있음'}")
                print(frm)
        os.startfile(archive.etf_xl)
        return False

def getTradingDate() -> dict:
    """
    가장 최근 거래일 기준 1W, 1M, 3M, 6M, 1Y 거래일 계산
    """
    td = datetime.strptime(tdt, "%Y%m%d")
    dm = lambda x:(td - timedelta(x)).strftime("%Y%m%d")
    label, delta = ['R1W', 'R1M', 'R3M', 'R6M', 'R1Y'], [7, 30, 91, 183, 365]
    return {l:krx.get_nearest_business_day_in_a_week(date=dm(d)) for l, d in zip(label, delta)}

def getCorpPerformance(tds:dict=None) -> pd.DataFrame:
    """
    보통주 기간별 수익률: 1Y 상장주식수 미변동 분
    :param tds: 기간 거래일
             R1D   R1W    R1M    R3M    R6M     R1Y
    종목코드
    095570  0.35  0.18   9.88   6.18  -4.22   42.82
    006840  3.39  1.91   8.10   2.64 -21.22  -25.48
    054620  1.26 -0.82   7.11  -8.02 -33.97   59.39
    ...      ...   ...    ...    ...    ...     ...
    000545 -0.37 -1.72  -2.20  -3.50 -16.67   20.12
    037440  0.44  0.11 -10.20  18.35  43.35  113.52
    238490  0.00 -3.17  -2.07  -0.84  -6.24  -27.43
    """
    if not isinstance(tds, dict) and not tds:
        tds = getTradingDate()

    keys, vals, objs = list(tds.keys()), list(tds.values()), dict()
    shares = pd.concat(objs={
        f'PREV': krx.get_market_cap_by_ticker(date=vals[-1], market='ALL', prev=True)['상장주식수'],
        f'CURR': krx.get_market_cap_by_ticker(date=tdt, market='ALL', prev=True)['상장주식수']
    }, axis=1)
    n_changed = shares[shares.PREV == shares.CURR].index

    for i in tqdm(range(len(tds) + 1), desc='기간별 수익률 계산(주식)'):
        if not i:
            df_today = krx.get_market_ohlcv_by_ticker(tdt, market='ALL')
            objs['R1D'] = round(df_today['등락률'], 2)
            continue
        objs[keys[i-1]] = krx.get_market_price_change(vals[i-1], tdt, market='ALL')['등락률']

    perf = pd.concat(objs=objs, axis=1, ignore_index=False)
    perf = perf[perf.index.isin(n_changed)]
    perf.index.name = '종목코드'
    return perf.round(2)

def getEtfPerformance(tds:dict=None) -> pd.DataFrame:
    """
    ETF 기간별 수익률: ETF는 신주 발행/증자 이슈 없음(2022.3.12 기준)
    :param tds: 기간 거래일
             R1D   R1W   R1M    R3M    R6M    R1Y
    종목코드
    152100 -0.19 -1.77 -3.86  -9.34 -11.23 -12.98
    295820  0.85 -0.79  0.71  -3.35 -10.40  -0.74
    253150 -0.30 -3.76 -7.61 -19.42 -23.88 -25.96
    ...      ...   ...   ...    ...    ...    ...
    176710  0.00 -0.31  0.05  -0.95  -1.43  -2.35
    140950 -0.81 -2.39 -3.89 -10.23 -12.29 -15.21
    419890  0.04  0.04   NaN    NaN    NaN    NaN
    """
    if not isinstance(tds, dict) and not tds:
        tds = getTradingDate()

    keys = ['R1D'] + list(tds.keys())
    vals = [(datetime.strptime(tdt, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")] + list(tds.values())
    iters = tqdm(dict(zip(keys, vals)).items(), desc='기간별 수익률 계산(ETF)')
    perf = pd.concat(
        objs={key:krx.get_etf_price_change_by_ticker(fromdate=val, todate=tdt)['등락률'] for key, val in iters},
        axis=1, ignore_index=False
    )
    perf.index.name = '종목코드'
    return perf.round(2)

def getIndexGroup(market:str) -> pd.DataFrame:
    """
    거래소 제공 지수
    :param market: KOSPI, KOSDAQ, KRX, THEME
                               종목명   지수분류
    종목코드
    1001                       코스피      KOSPI
    1002                코스피 대형주      KOSPI
    1003                코스피 중형주      KOSPI
     ...                          ...        ...
    1232      코스피 200 비중상한 20%      KOSPI
    1244     코스피200제외 코스피지수      KOSPI
    1894            코스피 200 TOP 10      KOSPI
    """
    if not market.lower() in ['kospi', 'kosdaq', 'krx', 'theme']:
        raise KeyError(f'Argument {market} not in [KOSPI, KOSDAQ, KRX, THEME]')
    tickers = krx.get_index_ticker_list(market='테마' if market == 'THEME' else market)
    return pd.DataFrame(data={
        '종목코드': tickers,
        '종목명': [krx.get_index_ticker_name(ticker) for ticker in tickers],
        '지수분류': [market] * len(tickers)
    }).set_index(keys='종목코드')

def getIndexMainDeposit(date: str):
    """
    코스피200, 코스닥150, 코스피중형주, 코스닥중형주, 코스피소형주 지수 포함 종목코드 관리
    :param date: 기준 일자
            지수코드         지수명      날짜
    종목코드
    005930      1028     코스피 200  20220312
    373220      1028     코스피 200  20220312
    000660      1028     코스피 200  20220312
    ...          ...            ...       ...
    088390      2003  코스닥 중형주  20220312
    097780      2003  코스닥 중형주  20220312
    025950      2003  코스닥 중형주  20220312
    """
    indices, objs = tqdm(['1028', '1003', '1004', '2203', '2003']), list()
    for index in tqdm(indices, desc='지수별 종목코드 수집'):
        indices.set_description(desc=f'Gathering {index} Deposits ...')
        tickers = krx.get_index_portfolio_deposit_file(ticker=index)
        df = pd.DataFrame(index=tickers)
        df['지수코드'] = index
        df['지수명'] = krx.get_index_ticker_name(index)
        df['날짜'] = date
        objs.append(df)
    depo = pd.concat(objs=objs, axis=0)
    depo.index.name = '종목코드'
    return depo


if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    # print(getWiseDate())
    # print(getCorpIPO())
    # print(getWiseGroup(name='WICS'))
    # print(getWiseGroup(name='WI26'))
    # print(getTradingDate())
    # print(getCorpPerformance())
    print(getEtfPerformance())
    # print(getThemeGroup())
    # print(getEtfGroup())
    # print(getIndexGroup(market='KOSPI'))
    # print(getIndexGroup(market='THEME'))
    # print(getIndexGroup(market='KRX'))
    # print(getIndexMainDeposit(date='20220312'))