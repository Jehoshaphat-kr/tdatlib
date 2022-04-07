import time, os
import pandas as pd
from tdatlib import archive, market_kr, ohlcv
from pykrx import stock as krx
from tqdm import tqdm


market = market_kr()
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

def __getPerformance(tickers) -> pd.DataFrame:
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

    add_tickers = [ticker for ticker in tickers if not ticker in perf.index]
    if add_tickers:
        process = tqdm(add_tickers)
        for n, ticker in enumerate(process):
            process.set_description(f'Fetch Returns - {ticker}')
            done = False
            while not done:
                try:
                    other = ohlcv(ticker=ticker, period=2).perf
                    perf = pd.concat(objs=[perf, other], axis=0, ignore_index=False)
                    done = True
                except ConnectionError as e:
                    time.sleep(0.5)
        perf.index.name = '종목코드'
        perf.to_csv(archive.performance, encoding='utf-8', index=True)
    return perf[perf.index.isin(tickers)]

def getMapName(category:str, sub_category:str=str()) -> str:
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
                     종목명      섹터        IPO    종가  ...    R1M    R3M    R6M     R1Y
    종목코드                                              ...
    096770     SK이노베이션    에너지 2007-07-25  209000  ...   0.96  -0.94 -12.29    4.21
    010950            S-Oil    에너지 1987-05-27   87800  ...   6.81   0.57 -13.50    9.48
    267250   현대중공업지주    에너지 2017-05-10   52700  ...   6.45  -8.65 -20.00   -6.38
    ...                 ...       ...        ...     ...  ...    ...    ...    ...     ...
    017390         서울가스  유틸리티 1995-08-18  186000  ...  -3.13  14.15   9.12  108.90
    117580       대성에너지  유틸리티 2010-12-24   12100  ...  23.08  17.65  31.29  124.30
    071320     지역난방공사  유틸리티 2010-01-29   36300  ...   4.46  -5.84 -13.78   -4.10
    """
    if not sub_category in [str(), '1028', '1003', '1004', '2203', '2003']:
        raise KeyError(f'입력 가능한 sub_category: 1028, 1003, 1004, 2203, 2003')

    base = __getCategory(category=category)
    line = market.etf_stat[['종목명', '종가', '시가총액']] if category == 'ETF' else market.icm
    baseline = base.join(other=line.drop(columns=['종목명']), how='left')

    if category.startswith('WI'):
        if sub_category:
            baseline = baseline[baseline.index.isin(krx.get_index_portfolio_deposit_file(ticker=sub_category))]
        else:
            baseline = baseline[baseline['시가총액'] > 300000000000]
    perf = __getPerformance(tickers=baseline.index)
    return baseline.join(other=perf, how='left')

def calcReduction(baseline:pd.DataFrame, category:str, sub_category:str=str()) -> tuple:
    """
    1차원 지도 데이터
    :param baseline:
    :param category: [str] WICS / WI26 / ETF / THEME
    :param sub_category: [str] 1028 / 1003 / 1004 / 2203 / 2003
                      종목코드          종목명    분류  ...        R6M        R1Y          크기
    0                   096770    SK이노베이션  에너지  ... -12.290000   4.210000  1.937154e+05
    1                   010950           S-Oil  에너지  ... -13.500000   9.480000  1.006490e+05
    2                   267250  현대중공업지주  에너지  ... -20.000000  -6.380000  4.202432e+04
    ..                     ...             ...     ...  ...        ...        ...           ...
    734  화장품,의류_WI26_전체     화장품,의류    전체  ... -17.736362 -16.019195  6.238694e+05
    735         화학_WI26_전체            화학    전체  ... -23.391283  -9.325348  1.052878e+06
    736              WI26_전체            전체          ...        NaN        NaN  2.258040e+07

    ['IT가전_WI26_전체', 'IT하드웨어_WI26_전체', ... , '화장품,의류_WI26_전체', '화학_WI26_전체']
    """
    frame = baseline.copy().reset_index(level=0)
    frame['크기'] = frame['시가총액'] / 100000000
    levels = [col for col in ['종목코드', '섹터', '산업'] if col in frame.columns]
    factors = [col for col in frame.columns if any([col.startswith(keyword) for keyword in ['R', 'B', 'P', 'D']])]
    map_name = getMapName(category=category, sub_category=sub_category)

    parent, bar = pd.DataFrame(), list()
    for n, level in enumerate(levels):
        if not n:
            child = frame.rename(columns={'섹터': '분류'})
            if '산업' in child.columns:
                child.drop(columns=['산업'], inplace=True)
        else:
            child = pd.DataFrame()
            layer = frame.groupby(levels[n:]).sum().reset_index()
            child["종목코드"] = layer[level] + f'_{category}_{map_name}'
            child["종목명"] = layer[level]
            child["분류"] = layer[levels[n + 1]] if n < len(levels) - 1 else map_name
            child["크기"] = layer[["크기"]]

            for name in child['종목명']:
                frm = frame[frame[level] == name]
                for f in factors:
                    if f == "DIV":
                        child.loc[child['종목명'] == name, f] = frm[f].mean() if not frm.empty else 0
                    else:
                        _t = frm[frm['PER'] != 0].copy() if f == 'PER' else frm
                        child.loc[child["종목명"] == name, f] = (_t[f] * _t['크기'] / _t['크기'].sum()).sum()
            if level == "섹터":
                bar = child["종목코드"].tolist()
        parent = pd.concat(objs=[parent, child], axis=0, ignore_index=True)

    cover = pd.DataFrame(
        data={'종목코드': f'{category}_{map_name}', '종목명': map_name, '분류': '', '크기': frame['크기'].sum()},
        index=['Cover']
    )
    map_data = pd.concat(objs=[parent, cover], axis=0, ignore_index=True)

    _t = map_data[map_data['종목명'] == map_data['분류']].copy()
    if not _t.empty:
        map_data.drop(index=_t.index, inplace=True)
    return map_data, bar

def calcColors(frame:pd.DataFrame, category:str) -> pd.DataFrame:
    """
    각 펙터 별 색상 결정(상대 비율)
    :param frame: 차원 축소 지도 데이터
    :param category: [str] WICS / WI26 / ETF / THEME
                      종목코드          종목명    분류  ...     CPBR     CPER     CDIV
    0                   096770    SK이노베이션  에너지  ...  #35764E  #414554  #F63538
    1                   010950           S-Oil  에너지  ...  #414554  #414554  #F63538
    2                   267250  현대중공업지주  에너지  ...  #30CC5A  #414554  #30CC5A
    ..                     ...             ...     ...  ...      ...      ...      ...
    735  화장품,의류_WI26_전체     화장품,의류    전체  ...  #414554  #F63538  #414554
    736         화학_WI26_전체            화학    전체  ...  #8B444E  #F63538  #8B444E
    737              WI26_전체            전체          ...  #C8C8C8  #C8C8C8  #C8C8C8
    """
    _ = 2.0  # 연간 무위험 수익
    limiter = {'R1Y': _, 'R6M': 0.5 * _, 'R3M': 0.25 * _, 'R1M': 0.08 * _, 'R1W': 0.02 * _, 'R1D': 0.005 * _}
    scale = ['#F63538', '#BF4045', '#8B444E', '#414554', '#35764E', '#2F9E4F', '#30CC5A']  # Low <---> High

    frm = frame.copy()
    colored = pd.DataFrame(index=frm.index)
    for t, lim in limiter.items():
        neu = frm[(-lim <= frm[t]) & (frm[t] < lim)].copy()
        neg, pos = frm[frm[t] < -lim].copy(), frm[lim <= frm[t]].copy()
        neg_val, pos_val = neg[t].sort_values(ascending=True).tolist(), pos[t].sort_values(ascending=True).tolist()
        neg_bin = 3 if len(neg_val) < 3 else [neg_val[int((len(neg_val) - 1) * _ / 3)] for _ in range(0, 4)]
        pos_bin = 3 if len(pos_val) < 3 else [pos_val[int((len(pos_val) - 1) * _ / 3)] for _ in range(0, 4)]
        n_color = pd.cut(neg[t], bins=neg_bin, labels=scale[:3], right=True)
        n_color.fillna(scale[0], inplace=True)
        p_color = pd.cut(pos[t], bins=pos_bin, labels=scale[4:], right=True)
        p_color.fillna(scale[4], inplace=True)
        u_color = pd.Series(dtype=str) if neu.empty else pd.Series(data=[scale[3]] * len(neu), index=neu.index)
        colors = pd.concat([n_color, u_color, p_color], axis=0)
        colors.name = f'C{t}'
        colored = colored.join(colors.astype(str), how='left')
        colored.fillna(scale[3], inplace=True)

    if not category == 'ETF':
        for f in ['PBR', 'PER', 'DIV']:
            re_scale = scale if f == 'DIV' else scale[::-1]
            value = frm[frm[f] != 0][f].dropna().sort_values(ascending=False)

            v = value.tolist()
            limit = [v[int(len(value) / 7) * i] for i in range(len(re_scale))] + [v[-1]]
            _color = pd.cut(value, bins=limit[::-1], labels=re_scale, right=True)
            _color.fillna(re_scale[0], inplace=True)
            _color.name = f"C{f}"
            colored = colored.join(_color.astype(str), how='left')

    frm = frm.join(colored, how='left')
    for col in colored.columns:
        frm.at[frm.index[-1], col] = '#C8C8C8'
    return frm

def calcPost(frame:pd.DataFrame, category:str, kosdaq:list=None):
    """
    지도 데이터 후처리
    :param frame: 직전 데이터프레임(색상 추가 데이터)
    :param category:
    :param kosdaq:
    :return:
    """
    if not kosdaq:
        kosdaq = krx.get_index_portfolio_deposit_file(ticker='2001')

    def rename(x):
        return x['종목명'] + "*" if x['종목코드'] in kosdaq else x['종목명']
    def reform_price(x):
        return '-' if x['종가'] == '-' else '{:,}원'.format(int(x['종가']))
    def reform_cap(x):
        return f"{x['크기']}억원" if len(x['크기']) < 5 else f"{x['크기'][:-4]}조 {x['크기'][-4:]}억원"

    frame = frame.copy()
    frame['종가'].fillna('-', inplace=True)
    frame['크기'] = frame['크기'].astype(int).astype(str)

    frame['종목명'] = frame.apply(rename, axis=1)
    frame['종가'] = frame.apply(reform_price, axis=1)
    frame['시가총액'] = frame.apply(reform_cap, axis=1)

    ns, cs = frame['종목명'].values, frame['분류'].values
    frame['ID'] = [f'{name}[{cs[n]}]' if name in ns[n + 1:] or name in ns[:n] else name for n, name in enumerate(ns)]

    for col in frame.columns:
        if col.startswith('P') or col.startswith('D') or col.startswith('R'):
            frame[col] = frame[col].apply(lambda v: round(v, 2))

    if not category == 'ETF':
        frame['PER'] = frame['PER'].apply(lambda val: val if not val == 0 else 'N/A')
    return frame

def isETFLatest(run:bool=True) -> bool:
    """
    ETF 관리 파일(Excel) 최신화 여부 :: openpyxl 필요 / Local 사용 권장
    """
    prev = pd.read_excel(archive.etf_xl, index_col='종목코드')
    prev.index = prev.index.astype(str).str.zfill(6)
    curr = market.etf_stat
    to_be_delete = prev[~prev.index.isin(curr.index)]
    to_be_update = curr[~curr.index.isin(prev.index)]
    if to_be_delete.empty and to_be_update.empty:
        return True
    else:
        for kind, frm in [('삭제', to_be_delete), ('추가', to_be_update)]:
            if not frm.empty:
                print("-" * 70, f"\n▷ ETF 분류 {kind} 필요 항목: {'없음' if frm.empty else '있음'}")
                print(frm)
        if run:
            os.startfile(archive.etf_xl)
        return False

def convertETFExcel2Csv():
    """
    ETF 관리 파일(Excel) 변환 (CSV)
    """
    df = pd.read_excel(archive.etf_xl, index_col='종목코드')
    df.index = df.index.astype(str).str.zfill(6)
    df.to_csv(archive.etf, index=True, encoding='utf-8')
    return

if __name__ == "__main__":

    t_category = 'WI26'
    t_sub_cate = ''
    # t_baseline = getBaseline(category=t_category)
    # print(t_baseline)

    # t_tree_data, t_bar_data = calcReduction(baseline=t_baseline, category=t_category, sub_category=t_sub_cate)
    # print(t_tree_data)
    # print(t_bar_data)

    # t_colored = calcColors(frame=t_tree_data, category=t_category)
    # print(t_colored)

    # t_treemap = calcPost(frame=t_colored, category=t_category)
    # print(t_treemap)

    isEtfLatest()
