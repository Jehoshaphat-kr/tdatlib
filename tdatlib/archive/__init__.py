import os
from datetime import datetime
from pytz import timezone


kst = datetime.now(timezone('Asia/Seoul'))
root = os.path.dirname(__file__)
etf = os.path.join(root, 'market/classify/etf.csv')
etf_xl = os.path.join(root, 'market/classify/__ETF.xlsx')
theme = os.path.join(root, 'market/classify/theme.csv')
wics = os.path.join(root, 'market/classify/wics.csv')
wi26 = os.path.join(root, 'market/classify/wi26.csv')
map_js = os.path.join(root, 'market/map/map-suffix.js')
deposit = os.path.join(root, 'market/general/deposit.csv')
icm = os.path.join(root, 'market/general/icm.csv')
perf = lambda x: os.path.join(root, f'market/performance/{x if x else kst.strftime("%Y%m%d")}perf.csv')


# noinspection PyBroadException
try:
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
except Exception:
    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')    

index_code = {
    '1028': '코스피200',
    '1003': '코스피 중형주',
    '1004': '코스피 소형주',
    '2203': '코스닥150',
    '2003': '코스닥 중형주'
}

wics_code = {
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

wi26_code = {
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

map_label = ['종목명', '종가', '시가총액', '크기',
             'R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y', 'PER', 'PBR', 'DIV',
             'CR1D', 'CR1W', 'CR1M', 'CR3M', 'CR6M', 'CR1Y', 'CPER', 'CPBR', 'CDIV']
