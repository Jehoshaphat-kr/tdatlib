from pandas_datareader import get_data_fred as fred
from datetime import datetime, timedelta
from tdatlib import toolbox
from tdatlib.macro._graph import _trace
import pandas as pd


class _fetch(object):

    KEY = "CEW3KQU603E6GA8VX0O9"
    __today  = datetime.now().date()
    __period = 20

    @property
    def period(self) -> int:
        return self.__period

    @period.setter
    def period(self, period:int):
        self.__period = period
        return


    @property
    def ecos_symbols(self) -> pd.DataFrame:
        """
        ECOS Symbol list

                코드                                 지표명 주기    발행처
        4    102Y004  본원통화 구성내역(평잔, 계절조정계열)    M  한국은행
        5    102Y002        본원통화 구성내역(평잔, 원계열)    M  한국은행
        6    102Y003  본원통화 구성내역(말잔, 계절조정계열)    M  한국은행
        ..       ...                                    ...   ..       ...
        794  251Y003                                    총량   A      None
        795  251Y002                          한국/북한 배율   A      None
        796  251Y001       북한의 경제활동별 실질 국내총생산   A  한국은행
        :return:
        """
        if not hasattr(self, '__codes'):
            url = f"http://ecos.bok.or.kr/api/StatisticTableList/{self.KEY}/xml/kr/1/10000/"
            df = toolbox.xml_to_df(url=url)
            df = df[df.SRCH_YN == 'Y'].copy()
            df['STAT_NAME'] = df.STAT_NAME.apply(lambda x: x[x.find(' ') + 1:])
            df = df.drop(columns='SRCH_YN')
            df = df.rename(columns={'STAT_CODE':'코드', 'STAT_NAME':'지표명', 'CYCLE':'주기', 'ORG_NAME':'발행처'})
            self.__setattr__('__codes', df)
        return self.__getattribute__('__codes')


    def fred(self, symbols:str or list):
        """
        Fetch data from Federal Reserve Economic Data | FRED | St. Louis Fed
        :param symbols : symbols
        :param period  : period
        :return:
        """
        start, end = self.__today - timedelta(self.__period * 365), self.__today
        if isinstance(symbols, str):
            symbols = [symbols]

        for symbol in symbols:
            if not hasattr(self, symbol):
                self.__setattr__(f'{symbol}{self.__period}', fred(symbols=symbol, start=start, end=end))
        return pd.concat(objs=[self.__getattribute__(f'{symbol}{self.__period}') for symbol in symbols], axis=1)


    def ecos(self, symbols:str or list) -> pd.DataFrame:
        """
        Fetch data from Economic Statistics System | ECOS | Korea Bank
        :param symbols : symbols
        :param period  : period
        :return:
        """
        if type(symbols) == str:
            symbols = [symbols]

        yy, ee = self.__today.year - self.__period, self.__today.year
        samples = self.ecos_symbols[self.ecos_symbols.코드.isin(symbols)]

        objs = list()
        for code, label, cyc in zip(samples.코드, samples.지표명, samples.주기):
            if not hasattr(self, f'_{code}'):
                s = f'{yy}0101' if cyc == 'D' else f'{yy}01S1' if cyc == 'SM' else f'{yy}01' if cyc == 'M' else f'{yy}{cyc}1'
                e = f'{ee}1230' if cyc == 'D' else f'{ee}12S1' if cyc == 'SM' else f'{ee}12' if cyc == 'M' else f'{ee}{cyc}12'
                url = f'http://ecos.bok.or.kr/api/StatisticSearch/{self.KEY}/xml/kr/1/100000/{code}/{cyc}/{s}/{e}'
                df = toolbox.xml_to_df(url=url)
                if cyc == 'M':
                    df['TIME'] = df['TIME'] + '15'

                _objs = list()
                for item in df['ITEM_NAME1'].drop_duplicates(keep='first'):
                    sr = df[df.ITEM_NAME1 == item].set_index(keys='TIME')['DATA_VALUE']
                    sr.name = item
                    _objs.append(sr)
                self.__setattr__(f'_{code}{self.__period}', pd.concat(objs=_objs, axis=1))

            objs.append(self.__getattribute__(f'_{code}{self.__period}'))
        return pd.concat(objs=objs, axis=1)


class data(_fetch):

    def __init__(self):
        self.trace = _trace(self)
        return

    @property
    def US_recession(self) -> list:
        return [
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

    @property
    def KR_recession(self) -> list:
        return [
            {'label': 'blank#01', 'from': datetime(1994, 11, 8), 'to': datetime(1995, 5, 27)},
            {'label': 'blank#02', 'from': datetime(1996, 5, 7), 'to': datetime(1997, 1, 7)},
            {'label': 'blank#03', 'from': datetime(1997, 8, 11), 'to': datetime(1997, 12, 12)},
            {'label': 'blank#04', 'from': datetime(1998, 3, 2), 'to': datetime(1998, 6, 16)},
            {'label': 'blank#05', 'from': datetime(1999, 1, 11), 'to': datetime(1999, 2, 24)},
            {'label': 'blank#06', 'from': datetime(1999, 7, 19), 'to': datetime(1999, 10, 5)},
            {'label': 'blank#07', 'from': datetime(2000, 1, 4), 'to': datetime(2000, 12, 22)},
            {'label': 'blank#08', 'from': datetime(2002, 4, 17), 'to': datetime(2003, 3, 17)},
            {'label': 'blank#09', 'from': datetime(2004, 4, 23), 'to': datetime(2004, 8, 2)},
            {'label': 'blank#10', 'from': datetime(2007, 11, 1), 'to': datetime(2008, 10, 24)},
            {'label': 'blank#11', 'from': datetime(2011, 5, 2), 'to': datetime(2011, 9, 26)},
            {'label': 'blank#12', 'from': datetime(2018, 1, 29), 'to': datetime(2019, 1, 3)},
            {'label': 'blank#13', 'from': datetime(2020, 1, 22), 'to': datetime(2020, 3, 19)},
            {'label': 'blank#14', 'from': datetime(2021, 7, 6), 'to': datetime(2022, 7, 6)},
        ]
    
    @property
    def 원달러환율(self) -> pd.DataFrame:
        raw = self.ecos(symbols=['731Y003'])
        rev = raw[[col for col in raw.columns if '달러' in col]]
        rev = rev.rename(columns={col: col[col.find('(') + 1:col.find(')')] for col in rev.columns})
        rev.index = pd.to_datetime(rev.index)
        return rev.astype(float)

    @property
    def 원위안환율(self) -> pd.DataFrame:
        raw = self.ecos(symbols=['731Y003'])
        rev = raw[[col for col in raw.columns if '위안' in col]]
        rev = rev.rename(columns={col: col[col.find('(') + 1:col.find(')')] for col in rev.columns})
        rev.index = pd.to_datetime(rev.index)
        return rev.astype(float)

    @property
    def 한국금리(self) -> pd.DataFrame:
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
    def NSI(self) -> pd.DataFrame:
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
    def 한국경상수지(self) -> pd.DataFrame:
        raw = self.ecos(symbols='301Y017')
        rev = raw['경상수지']
        rev.index = pd.to_datetime(rev.index)
        return rev

    @property
    def 미국금리(self) -> pd.DataFrame:
        if not hasattr(self, '__미국금리'):
            cols = {
                "DFF": "기준금리",
                "DGS3MO": "3개월물",
                "DGS2": "2년물",
                "DGS10": "10년물",
                "DFII10": "10년물w기대인플레이션",
                "T10Y3M": "10년-3개월금리차",
                "T10Y2Y": "10년-2년금리차",
                "BAMLH0A0HYM2": "하이일드스프레드",
                "MORTGAGE30US": "30년모기지",
            }
            raw = self.fred(symbols=list(cols.keys()))
            raw = raw.rename(columns=cols)
            self.__setattr__('__미국금리', raw)
        return self.__getattribute__('__미국금리')

    @property
    def 미국물가(self) -> pd.DataFrame:
        cols = {
            'T5YIFR': '5년기대인플레이션',
            'T10YIE': '10년평형인플레이션',
            'CPIAUCSL': '소비자물가지수',
        }
        raw = self.fred(symbols=list(cols.keys()))
        raw = raw.rename(columns=cols)
        return raw

    @property
    def 국제유가(self) -> pd.DataFrame:
        cols = {
            'DCOILBRENTEU':'BRENT유',
            'DCOILWTICO': 'WTI유',
        }
        raw = self.fred(symbols=list(cols.keys()))
        raw = raw.rename(columns=cols)
        return raw


if __name__ == "__main__":
    import plotly.graph_objects as go
    pd.set_option('display.expand_frame_repr', False)

    app = data()
    app.period = 90

    print(app.미국금리)
    print(app.미국금리['3개월물'])
    # print(app.한국금리)
    # print(app.원달러환율)

