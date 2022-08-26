from pandas_datareader import get_data_fred as fred
from datetime import datetime, timedelta
from tdatlib import toolbox
import pandas as pd
import inspect


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
        Fetch src from Federal Reserve Economic Data | FRED | St. Louis Fed
        :param symbols : symbols
        :param period  : period
        :return:
        """
        start, end = self.__today - timedelta(self.__period * 365), self.__today
        if isinstance(symbols, str):
            symbols = [symbols]

        for symbol in symbols:
            if not hasattr(self, f'{symbol}{self.__period}'):
                self.__setattr__(f'{symbol}{self.__period}', fred(symbols=symbol, start=start, end=end))
        return pd.concat(objs=[self.__getattribute__(f'{symbol}{self.__period}') for symbol in symbols], axis=1)


    def ecos(self, symbols:str or list) -> pd.DataFrame or pd.Series:
        """
        Fetch src from Economic Statistics System | ECOS | Korea Bank
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
            if not hasattr(self, f'_{code}{self.__period}'):
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

                df = pd.concat(objs=_objs, axis=1)
                df.index = pd.to_datetime(df.index.tolist())
                self.__setattr__(f'_{code}{self.__period}', df)

            objs.append(self.__getattribute__(f'_{code}{self.__period}'))
        return pd.concat(objs=objs, axis=1)


class data(_fetch):

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
    def KRW_USD_exchange(self) -> pd.DataFrame:
        raw = self.ecos(symbols=['731Y003'])
        rev = raw[[col for col in raw.columns if '달러' in col]]
        rev = rev.rename(columns={col: col[col.find('(') + 1:col.find(')')] for col in rev.columns})
        rev.index = pd.to_datetime(rev.index)
        return rev.astype(float)

    @property
    def KRW_CHY_exchange(self) -> pd.DataFrame:
        raw = self.ecos(symbols=['731Y003'])
        rev = raw[[col for col in raw.columns if '위안' in col]]
        rev = rev.rename(columns={col: col[col.find('(') + 1:col.find(')')] for col in rev.columns})
        rev.index = pd.to_datetime(rev.index)
        return rev.astype(float)

    def __getter__(self, code:str, label:str, name:str) -> pd.Series:
        if label:
            _ = self.ecos(symbols=code)[label]
            _.name = name
            return _
        else:
            return self.fred(symbols=code).rename(columns={code:name})

    @property
    def KR_IR(self) -> pd.Series:
        return self.__getter__('722Y001', '한국은행 기준금리', inspect.currentframe().f_code.co_name)
        # return self.ecos(symbols='722Y001')["한국은행 기준금리"].rename(columns={"한국은행 기준금리":inspect.currentframe().f_code.co_name})

    @property
    def KR_3M_CD(self) -> pd.Series:
        return self.ecos(symbols='722Y001')["CD(91일)"].rename(columns={"CD(91일)": inspect.currentframe().f_code.co_name})

    @property
    def KR_3M_CP(self) -> pd.Series:
        return self.ecos(symbols='722Y001')["CP(91일)"].rename(columns={"CP(91일)": inspect.currentframe().f_code.co_name})

    @property
    def KR_2Y_TY(self) -> pd.Series:
        return self.ecos(symbols='817Y002')["국고채(2년)"].rename(columns={"국고채(2년)": inspect.currentframe().f_code.co_name})

    @property
    def KR_10Y_TY(self) -> pd.Series:
        return self.ecos(symbols='817Y002')["국고채(10년)"].rename(columns={"국고채(2년)": inspect.currentframe().f_code.co_name})

    @property
    def KR_3Y_CB_AAm(self) -> pd.Series:
        return self.ecos(symbols='817Y002')["회사채(3년, AA-)"].rename(columns={"회사채(3년, AA-)": inspect.currentframe().f_code.co_name})

    @property
    def KR_3Y_CB_BBBm(self) -> pd.Series:
        return self.ecos(symbols='817Y002')["회사채(3년, BBBA-)"].rename(columns={"회사채(3년, BBB-)": inspect.currentframe().f_code.co_name})

    @property
    def KR_NSI(self) -> pd.Series:
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
        return self.ecos(symbols='521Y001')

    @property
    def US_IR(self) -> pd.Series:
        return self.fred(symbols="DFF").rename(columns={"DFF": inspect.currentframe().f_code.co_name})

    @property
    def US_3M_TY(self) -> pd.Series:
        return self.fred(symbols="DGS3MO").rename(columns={"DGS3MO": inspect.currentframe().f_code.co_name})

    @property
    def US_2Y_TY(self) -> pd.Series:
        return self.fred(symbols="DGS2").rename(columns={"DGS2": inspect.currentframe().f_code.co_name})

    @property
    def US_10Y_TY(self) -> pd.Series:
        return self.fred(symbols="DGS10").rename(columns={"DGS10": inspect.currentframe().f_code.co_name})

    @property
    def US_10Y_TY_Inflation(self) -> pd.Series:
        return self.fred(symbols="DFII10").rename(columns={"DFII10": inspect.currentframe().f_code.co_name})

    @property
    def US_10Y3M_dTY(self) -> pd.Series:
        return self.fred(symbols="T10Y3M").rename(columns={"T10Y3M": inspect.currentframe().f_code.co_name})

    @property
    def US_10Y2Y_dTY(self) -> pd.Series:
        return self.fred(symbols="T10Y2Y").rename(columns={"T10Y2Y": inspect.currentframe().f_code.co_name})

    @property
    def US_HY_Spread(self) -> pd.Series:
        return self.fred(symbols="BAMLH0A0HYM2").rename(columns={"T10Y2Y": inspect.currentframe().f_code.co_name})

    @property
    def US_5Y_BEI(self) -> pd.Series:
        return self.fred(symbols="T5YIFR").rename(columns={'T5YIFR': inspect.currentframe().f_code.co_name})

    @property
    def US_10Y_BEI(self) -> pd.Series:
        return self.fred(symbols='T10YIE').rename(columns={'T10YIE': inspect.currentframe().f_code.co_name})

    @property
    def US_CPI(self) -> pd.Series:
        return self.fred(symbols='CPIAUCSL').rename(columns={'CPIAUCSL': inspect.currentframe().f_code.co_name})

    @property
    def Oil_Brent(self) -> pd.Series:
        return self.fred(symbols='DCOILBRENTEU').rename(columns={'DCOILBRENTEU':'BRENT유'})

    @property
    def Oil_WTI(self) -> pd.Series:
        return self.fred(symbols='DCOILWTICO').rename(columns={'DCOILWTICO': 'WTI유'})

    @property
    def properties(self) -> list:
        exclude =[
            'properties',
            'KEY',
            'period',
            'ecos_symbols',
            'fred',
            'ecos',
            'describe'
        ]
        return [elem for elem in self.__dir__() if not elem.startswith('_') and not elem in exclude]

    def describe(self):
        for e in self.properties:
            print(e)
        return

if __name__ == "__main__":
    import plotly.graph_objects as go
    pd.set_option('display.expand_frame_repr', False)

    app = data()
    app.period = 90

    print(app.KR_IR)

