import pandas as pd
import requests, time, json, os
import urllib.request as req
from tdatlib import archive
from tqdm import tqdm
from pytz import timezone
from datetime import datetime, timedelta
from pykrx import stock as krx


kst = datetime.now(timezone('Asia/Seoul'))
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
    for code, name in tqdm(codes.items(), desc=f'Fetch {name}'):
        url = f'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={date}&sec_cd={code}'
        while True:
            # noinspection PyBroadException
            try:
                load = requests.get(url).json()
                data = [[_['CMP_CD'], _['CMP_KOR'], _['SEC_NM_KOR'], _['IDX_NM_KOR'][5:]] for _ in load['list']]
                break
            except:
                print(f'\t- Parse error while fetching WISE INDEX {code} {name}')
                time.sleep(1)
        frame = pd.concat(
            objs=[frame, pd.DataFrame(data=data, columns=['종목코드', '종목명', '산업', '섹터'])],
            axis=0, ignore_index=True
        )
    frame['날짜'] = date
    if name.lower() == 'wi26':
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

def getCorpPerformance() -> pd.DataFrame:
    """
    보통주 기간별 수익률: 1Y 상장주식수 미변동 분
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
    t_today = kst.strftime("%Y%m%d")
    t_label = ['R1W', 'R1M', 'R3M', 'R6M', 'R1Y']
    t_stamp = [(kst - timedelta(days)).strftime("%Y%m%d") for days in [7, 30, 91, 183, 365]]
    shares = pd.concat(objs={
        f'PREV': krx.get_market_cap_by_ticker(date=t_stamp[-1], market='ALL', prev=True)['상장주식수'],
        f'CURR': krx.get_market_cap_by_ticker(date=t_today, market='ALL', prev=True)['상장주식수']
    }, axis=1)

    objs = {'R1D': round(krx.get_market_ohlcv(t_today, market='ALL', prev=True)['등락률'], 2)}
    objs.update(
        {label:krx.get_market_price_change(t, t_today, market='ALL')['등락률'] for label, t in zip(t_label, t_stamp)}
    )
    perf = pd.concat(objs=objs, axis=1, ignore_index=False)
    perf = perf[perf.index.isin(shares[shares.PREV == shares.CURR].index)]
    perf.index.name = '종목코드'
    return perf

def getEtfPerformance() -> pd.DataFrame:
    """
    ETF 기간별 수익률: ETF는 신주 발행/증자 이슈 없음(2022.3.12 기준)
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
    df_today, t_today, cnt = krx.get_etf_ohlcv_by_ticker(date=kst.strftime("%Y%m%d")), kst, 1
    while df_today.empty:
        t_today = kst - timedelta(cnt)
        df_today = krx.get_etf_ohlcv_by_ticker(date=t_today.strftime("%Y%m%d"))
        cnt += 1
    objs = {'기준': df_today['종가']}

    t_label= ['R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y']
    t_stamp = [t_today - timedelta(days) for days in [1, 7, 30, 91, 183, 365]]
    for label, date in zip(t_label, t_stamp):
        re_date, cnt = date, 1
        df = krx.get_etf_ohlcv_by_ticker(date=re_date.strftime("%Y%m%d"))
        while df.empty:
            re_date -= timedelta(cnt)
            df = krx.get_etf_ohlcv_by_ticker(date=re_date.strftime("%Ym%d"))
            cnt += 1
        objs[f'P-{label}'] = df['종가']
    perf = pd.concat(objs=objs, axis=1, ignore_index=False)
    perf.index.name = '종목코드'

    for label in t_label:
        perf[label] = round(100 * (perf['기준']/perf[f'P-{label}'] - 1), 2)
    perf = perf[perf.index.isin(df_today.index)]
    return perf.drop(columns=['기준'] + [f'P-{label}' for label in t_label])

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
    for index in indices:
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
    # print(getCorpPerformance())
    print(getEtfPerformance())
    # print(getThemeGroup())
    # print(getEtfGroup())
    # print(getIndexGroup(market='KOSPI'))
    # print(getIndexGroup(market='THEME'))
    # print(getIndexGroup(market='KRX'))
    # print(getIndexMainDeposit(date='20220312'))