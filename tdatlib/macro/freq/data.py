from tdatlib.macro.core import fetch
from datetime import datetime
import pandas as pd


class data(fetch):

    recession_us = [
        {'label': 'The Own Goal Recession', 'from': datetime(1937, 5, 1), 'to': datetime(1938, 6, 1)},
        {'label': 'The V-Day Recession', 'from': datetime(1945, 2, 1), 'to': datetime(1945, 10, 1)},
        {'label': 'The Post-War Brakes Tap Recession', 'from': datetime(1948, 11, 1), 'to': datetime(1949, 10, 1)},
        {'label': 'Post-Korean War Recession', 'from': datetime(1953, 7, 1), 'to': datetime(1954, 5, 1)},
        {'label': 'The Investment Bust Recession', 'from': datetime(1957, 8, 1), 'to': datetime(1958, 4, 1)},
        {'label': 'The Rolling Adjustment Recession', 'from': datetime(1960, 4, 1), 'to': datetime(1961, 2, 1)},
        {'label': 'The Guns and Butter Recession', 'from': datetime(1969, 12, 1), 'to': datetime(1970, 11, 1)},
        {'label': 'The Oil Embargo Recession', 'from': datetime(1973, 11, 1), 'to': datetime(1975, 3, 1)},
        {'label': 'The Iran and Volcker Recession', 'from': datetime(1980, 1, 1), 'to': datetime(1980, 7, 1)},
        {'label': 'Double-Dip Recession', 'from': datetime(1981, 7, 1), 'to': datetime(1982, 11, 1)},
        {'label': 'The Gulf War Recession', 'from': datetime(1990, 7, 1), 'to': datetime(1991, 3, 1)},
        {'label': 'The Dot-Bomb Recession', 'from': datetime(2001, 3, 1), 'to': datetime(2001, 11, 1)},
        {'label': 'The Great Recession', 'from': datetime(2007, 12, 1), 'to': datetime(2009, 6, 1)},
        {'label': 'The COVID-19 Recession', 'from': datetime(2020, 2, 1), 'to': datetime(2020, 4, 1)},
    ]


    recession_kr = [
        {'label': 'blank#01', 'from': datetime(1994, 11, 8), 'to': datetime(1995, 5, 27)},
        {'label': 'blank#02', 'from': datetime(1996, 5, 13), 'to': datetime(1997, 1, 7)},
        {'label': 'blank#03', 'from': datetime(1996, 6, 17), 'to': datetime(1997, 12, 12)},
        {'label': 'blank#04', 'from': datetime(1998, 3, 2), 'to': datetime(1998, 6, 16)},
        {'label': 'blank#05', 'from': datetime(1999, 1, 11), 'to': datetime(1999, 2, 24)},
        {'label': 'blank#06', 'from': datetime(1999, 7, 19), 'to': datetime(1999, 10, 5)},
        {'label': 'blank#07', 'from': datetime(2000, 1, 4), 'to': datetime(2000, 12, 22)},
        {'label': 'blank#08', 'from': datetime(2002, 4, 17), 'to': datetime(2003, 3, 17)},
        {'label': 'blank#09', 'from': datetime(2004, 4, 23), 'to': datetime(2004, 8, 2)},
        {'label': 'blank#10', 'from': datetime(2004, 4, 23), 'to': datetime(2004, 8, 2)},
        {'label': 'blank#11', 'from': datetime(2007, 11, 1), 'to': datetime(2008, 10, 24)},
        {'label': 'blank#12', 'from': datetime(2011, 5, 2), 'to': datetime(2011, 9, 26)},
        {'label': 'blank#13', 'from': datetime(2018, 1, 29), 'to': datetime(2019, 1, 3)},
        {'label': 'blank#14', 'from': datetime(2020, 1, 22), 'to': datetime(2020, 3, 19)},
        {'label': 'blank#15', 'from': datetime(2021, 7, 6), 'to': datetime(2022, 7, 6)},
    ]


    @property
    def ecos_usd2krw(self) -> pd.DataFrame:
        """
        Frequently Used ECOS :: 원 / 달러 환율
        """
        raw = self.ecos(symbols=['731Y003'])
        rev = raw[[col for col in raw.columns if '달러' in col]]
        rev = rev.rename(columns={col: col[col.find('(') + 1:col.find(')')] for col in rev.columns})
        rev.index = pd.to_datetime(rev.index)
        return rev

    @property
    def ecos_cny2krw(self) -> pd.DataFrame:
        """
        Frequently Used ECOS :: 원 / 위안 환율
        """
        raw = self.ecos(symbols=['731Y003'])
        rev = raw[[col for col in raw.columns if '위안' in col]]
        rev = rev.rename(columns={col: col[col.find('(') + 1:col.find(')')] for col in rev.columns})
        rev.index = pd.to_datetime(rev.index)
        return rev

    @property
    def ecos_interest_rate(self) -> pd.DataFrame:
        """
        Frequently Used ECOS :: 국내 금리
        """
        cols = {
            "자금조정 예금금리": "예금금리",
            "자금조정 대출금리": "대출금리",
            "한국은행 기준금리": "기준금리",
            "콜금리(1일, 전체거래)": "콜금리1D",
            "CD(91일)": "CD금리91D",
            "CP(91일)": "CP금리91D",
            "국고채(2년)": "국고채2Y",
            "국고채(3년)": "국고채3Y",
            "국고채(5년)": "국고채5Y",
            "국고채(10년)": "국고채10Y",
            "국고채(30년)": "국고채20Y",
            "회사채(3년, AA-)": "회사채3YAA-",
            "회사채(3년, BBB-)": "회사채3YBBB-",
        }
        raw = self.ecos(symbols=['722Y001', '817Y002'])
        rev = raw[list(cols.keys())].rename(columns=cols)
        rev.index = pd.to_datetime(rev.index)
        return rev

    @property
    def ecos_nsi(self) -> pd.DataFrame:
        """
        Frequently Used ECOS :: 뉴스심리지수[한국은행]
        한국은행은 경제분야 뉴스기사에 나타난 경제심리를 지수화한 뉴스심리지수(NSI)를 ECOS에 실험적으로 공개

        - 포털사이트의 경제분야 뉴스기사를 기반으로 표본문장을 추출
        - 각 문장에 나타난 긍정, 부정, 중립의 감성을 기계학습 방법으로 분류
        - 긍정과 부정 문장수의 차이를 계산하여 지수화한 지표

        * 지수 작성대상 표본은 ’05년 이후 50여개 언론사의 경제분야 뉴스기사 문장으로,
          일별 10,000개의 표본문장을 무작위로 추출하였음.

        * ’05.1.1~’22.1.31일중 일별 뉴스심리지수를 작성한 결과,
          장기평균치 100을 기준으로 대체로 대칭적인 흐름을 보이는 가운데 경제심리의 변화를 신속하게 포착됨.
        """
        raw = self.ecos(symbols='521Y001')
        raw.index = pd.to_datetime(raw.index)
        return raw

    @property
    def ecos_current_account(self) -> pd.DataFrame:
        """
        Frequently Used ECOS :: 경상 수지 Balance On Current Account
        경상수지가 흑자라는 것은 상품과 서비스 등의 수출과 관련해 늘어나는 생산과 일자리가 수입으로 인해 줄어드는 것보다
        크다는 것을 의미한다. 때문에 그만큼 국민의 소득 수준이 높아지고 고용이 확대되는 긍정적인 효과가 있다.

        반대로 경상수지가 적자를 나타내는 경우 소득 수준이 낮아지고 실업이 늘어남과 동시에 외채가 늘어나면서 대외신인도가
        하락하게 된다. 나아가 국내외 여건 악화로 자본유입이 급격히 둔화되거나 대규모 자본유출이 나타날 경우 외화 유동성
        부족으로 외환위기에 이르게 될 가능성이 높아진다.
        """
        raw = self.ecos(symbols='301Y017')
        rev = raw['경상수지']
        rev.index = pd.to_datetime(rev.index)
        return rev