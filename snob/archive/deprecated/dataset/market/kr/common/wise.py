from tqdm import tqdm
import pandas as pd
import requests, time, os


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATE = str()
URL_BASE = 'http://www.wiseindex.com/Index/Index#/G1010.0.Components'
URL_WISE = 'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt=%s&sec_cd=%s'
DIR_THM  = f'{ROOT}/_archive/category/theme.csv'
DIR_WICS = f'{ROOT}/_archive/category/wics.csv'
DIR_WI26 = f'{ROOT}/_archive/category/wi26.csv'
CD_WICS = {
    'G1010': '에너지',
    'G1510': '소재',
    'G2010': '자본재',
    'G2020': '상업서비스와공급품',
    'G2030': '운송',
    'G2510': '자동차와부품',
    'G2520': '내구소비재와의류',
    'G2530': '호텔,레스토랑,레저 등',
    'G2550': '소매(유통)',
    'G2560': '교육서비스',
    'G3010': '식품과기본식료품소매',
    'G3020': '식품,음료,담배',
    'G3030': '가정용품과개인용품',
    'G3510': '건강관리장비와서비스',
    'G3520': '제약과생물공학',
    'G4010': '은행',
    'G4020': '증권',
    'G4030': '다각화된금융',
    'G4040': '보험',
    'G4050': '부동산',
    'G4510': '소프트웨어와서비스',
    'G4520': '기술하드웨어와장비',
    'G4530': '반도체와반도체장비',
    'G4535': '전자와 전기제품',
    'G4540': '디스플레이',
    'G5010': '전기통신서비스',
    'G5020': '미디어와엔터테인먼트',
    'G5510': '유틸리티'
}

CD_WI26 = {
    'WI100': '에너지',
    'WI110': '화학',
    'WI200': '비철금속',
    'WI210': '철강',
    'WI220': '건설',
    'WI230': '기계',
    'WI240': '조선',
    'WI250': '상사,자본재',
    'WI260': '운송',
    'WI300': '자동차',
    'WI310': '화장품,의류',
    'WI320': '호텔,레저',
    'WI330': '미디어,교육',
    'WI340': '소매(유통)',
    'WI400': '필수소비재',
    'WI410': '건강관리',
    'WI500': '은행',
    'WI510': '증권',
    'WI520': '보험',
    'WI600': '소프트웨어',
    'WI610': 'IT하드웨어',
    'WI620': '반도체',
    'WI630': 'IT가전',
    'WI640': '디스플레이',
    'WI700': '통신서비스',
    'WI800': '유틸리티',
}


def __fetchByGroup(group_name:str, group_codes:dict, wise_date:str=str()) -> pd.DataFrame:
    loop, frame = tqdm(group_codes.items()), pd.DataFrame()
    for code, label in loop:
        loop.set_description(desc=f'{group_name} / ({code}){label}...')
        while True:
            # noinspection PyBroadException
            try:
                data = [[_['CMP_CD'], _['CMP_KOR'], _['SEC_NM_KOR'], _['IDX_NM_KOR'][5:]]
                        for _ in requests.get(URL_WISE % (wise_date, code)).json()['list']]
                fetch = pd.DataFrame(data=data, columns=['종목코드', '종목명', '산업', '섹터'])
                break
            except:
                print(f'\t- Parse error while fetching WISE INDEX {code} {label}')
                time.sleep(1)
        frame = pd.concat(objs=[frame, fetch], axis=0, ignore_index=True)
    frame['날짜'] = wise_date
    return frame.set_index(keys='종목코드')


def __fetchWiseDate() -> str:
    src = requests.get(url=URL_BASE).text
    tic = src.find("기준일")
    toc = tic + src[tic:].find("</p>")
    return src[tic + 6: toc].replace('.', '')


def fetch_wics() -> pd.DataFrame:
    global DATE
    if not DATE:
        DATE = __fetchWiseDate()
    fetch = pd.read_csv(DIR_WICS, index_col='종목코드', encoding='utf-8')
    fetch.index = fetch.index.astype(str).str.zfill(6)
    if not str(fetch['날짜'][0]) == DATE:
        fetch = __fetchByGroup(group_name='WICS', group_codes=CD_WICS, wise_date=DATE)
        fetch.to_csv(DIR_WICS, index=True, encoding='utf-8')
    return fetch.drop(columns=['날짜'])


def fetch_wi26() -> pd.DataFrame:
    global DATE
    if not DATE:
        DATE = __fetchWiseDate()
    fetch = pd.read_csv(DIR_WI26, index_col='종목코드', encoding='utf-8')
    fetch.index = fetch.index.astype(str).str.zfill(6)
    if not str(fetch['날짜'][0]) == DATE:
        fetch = __fetchByGroup(group_name='WI26', group_codes=CD_WI26, wise_date=DATE)
        fetch.drop(columns=['산업'], inplace=True)
        fetch.to_csv(DIR_WI26, index=True, encoding='utf-8')
    return fetch.drop(columns=['날짜'])

def read_theme() -> pd.DataFrame:
    df = pd.read_csv(DIR_THM, index_col='종목코드')
    df.index = df.index.astype(str).str.zfill(6)
    return df
