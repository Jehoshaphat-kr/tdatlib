import time, os
import pandas as pd
from tdatlib import archive, market, stock
from pykrx import stock as krx
from tqdm import tqdm


market = market()
def __getCategory(category:str) -> pd.DataFrame:
    """
    분류에 따른 데이터 수집
    :param category: [str] WICS / WI26 / ETF / THEME
    """
    if not category in ['WICS', 'WI26', 'ETF', 'THEME']:
        raise KeyError(f'입력 가능한 category: WICS, WI26, ETF, THEME')

    if category == 'WICS':
        return market.wics
    if category == 'WI26':
        return market.wi26
    if category == 'ETF':
        return market.etf_group
    if category == 'THEME':
        return market.theme

def __getMapName(category:str, sub_category:str=str()) -> str:
    """
    분류에 따른 데이터 수집
    :param category: [str] WICS / WI26 / ETF / THEME
    :param sub_category: [str] 1028 / 1003 / 1004 / 2203 / 2003
    """
    if not category in ['WICS', 'WI26', 'ETF', 'THEME']:
        raise KeyError(f'입력 가능한 category: WICS, WI26, ETF, THEME')

    if not sub_category in [str(), '1028', '1003', '1004', '2203', '2003']:
        raise KeyError(f'입력 가능한 sub_category: 1028, 1003, 1004, 2203, 2003')

    if sub_category:
        # 코스피200(1028), 코스피 중형주(1003), 코스피 소형주(1004), 코스닥150(2203), 코스닥 중형주(2003)
        return archive.index_code[sub_category]
    if category.startswith('WI'):
        return '전체'
    if category == 'THEME':
        return '테마'
    if category == 'ETF':
        return category

def getBaseline(category:str, sub_category:str=str()):
    """
    분류 + 기본 정보 및 sub_category(시가총액) 별 종목 제한
    :param category: [str] WICS / WI26 / ETF / THEME
    :param sub_category: [str] 1028 / 1003 / 1004 / 2203 / 2003
                    종목명      산업      섹터        IPO  ...       PBR      EPS       DIV      DPS
    종목코드                                          ...
    096770    SK이노베이션    에너지    에너지 2007-07-25  ...  1.360352      0.0  0.000000      0.0
    010950           S-Oil    에너지    에너지 1987-05-27  ...  1.830078      0.0  0.000000      0.0
    267250  현대중공업지주    에너지    에너지 2017-05-10  ...  0.589844      0.0  7.058594   3700.0
    ...                ...       ...       ...        ...  ...       ...      ...       ...      ...
    017390        서울가스  유틸리티  유틸리티 1995-08-18  ...  0.899902  33732.0  9.046875  16750.0
    117580      대성에너지  유틸리티  유틸리티 2010-12-24  ...  1.080078    514.0  2.019531    250.0
    071320    지역난방공사  유틸리티  유틸리티 2010-01-29  ...  0.229980   2279.0  2.689453    965.0
    """
    if not sub_category in [str(), '1028', '1003', '1004', '2203', '2003']:
        raise KeyError(f'입력 가능한 sub_category: 1028, 1003, 1004, 2203, 2003')

    base = __getCategory(category=category)
    line = market.etf_stat[['종가', '시가총액']] if category == 'ETF' else market.icm
    baseline = base.join(other=line.drop(columns=['종목명']), how='left')

    if category.startswith('WI'):
        if sub_category:
            return baseline[baseline.index.isin(krx.get_index_portfolio_deposit_file(ticker=sub_category))]
        return baseline[baseline['시가총액'] > 300000000000]
    return baseline

def getPerformance(tickers) -> pd.DataFrame:
    """
    종목 기간별 수익률
             R1D   R1W    R1M    R3M    R6M    R1Y
    종목코드
    031330 -2.64 -3.37  -1.27 -18.42 -21.24  38.39
    042670 -2.85 -1.37   2.05 -15.65 -45.68  -6.20
    122870 -1.62  6.84  18.25  -2.56   3.75  29.85
    ...      ...   ...    ...    ...    ...    ...
    302440 -6.80 -7.43 -25.95 -42.80 -59.17    NaN
    006400 -6.01 -7.36 -24.56 -29.99 -33.59 -34.60
    002790 -0.94  1.40  12.65   2.39 -13.87 -25.08
    """
    if not os.path.isfile(archive.performance):
        _ = market.performance
    perf = pd.read_csv(archive.performance, encoding='utf-8', index_col='종목코드')
    perf.index = perf.index.astype(str).str.zfill(6)

    tickers = [ticker for ticker in tickers if not ticker in perf.index]
    if tickers:
        process = tqdm(tickers)
        for n, ticker in enumerate(process):
            process.set_description(f'Fetch Returns - {ticker}')
            done = False
            while not done:
                try:
                    other = stock(ticker=ticker, period=2, name=ticker).perf
                    perf = pd.concat(objs=[perf, other], axis=0, ignore_index=False)
                    done = True
                except ConnectionError as e:
                    time.sleep(0.5)

        perf.index.name = '종목코드'
        perf.to_csv(archive.performance, encoding='utf-8', index=True)
    return perf


if __name__ == "__main__":

    baseline = getBaseline(category='WICS')
    perform = getPerformance(tickers=baseline.index)
    # print(basline)
    print(perform)