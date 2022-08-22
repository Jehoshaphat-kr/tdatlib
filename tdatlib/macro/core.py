from pandas_datareader import get_data_fred as fred
from datetime import datetime, timedelta
from tdatlib import toolbox
import pandas as pd


class fetch(object):

    KEY = "CEW3KQU603E6GA8VX0O9"

    def __init__(self):
        self.today = datetime.now().date()
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


    def fred(self, symbols:str or list, period:int = 10):
        """
        Fetch data from Federal Reserve Economic Data | FRED | St. Louis Fed
        :param symbols : symbols
        :param period  : period
        :return:
        """
        start, end = self.today - timedelta(period * 365), self.today
        if isinstance(symbols, str):
            symbols = [symbols]

        for symbol in symbols:
            if not hasattr(self, symbol):
                self.__setattr__(symbol, fred(symbols=symbol, start=start, end=end))
        return pd.concat(objs=[self.__getattribute__(symbol) for symbol in symbols], axis=1)


    def ecos(self, symbols:str or list, period:int = 10) -> pd.DataFrame:
        """
        Fetch data from Economic Statistics System | ECOS | Korea Bank
        :param symbols : symbols
        :param period  : period
        :return:
        """
        if type(symbols) == str:
            symbols = [symbols]

        yy, ee = self.today.year - period, self.today.year
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
                self.__setattr__(f'_{code}', pd.concat(objs=_objs, axis=1))

            objs.append(self.__getattribute__(f'_{code}'))
        return pd.concat(objs=objs, axis=1)


class fetch_ecos(object):


    def __init__(self):
        return





    @property
    def krw_usd(self) -> pd.DataFrame:
        """
        원 / 달러 환율
        """
        raw = self.fetch(codes=['731Y003'])
        rev = raw[[col for col in raw.columns if '달러' in col]]
        rev = rev.rename(columns={col:col[col.find('(') + 1:col.find(')')] for col in rev.columns})
        rev.index = pd.to_datetime(rev.index)
        return rev

    @property
    def krw_cny(self) -> pd.DataFrame:
        """
        원 / 위안 환율
        """
        raw = self.fetch(codes=['731Y003'])
        rev = raw[[col for col in raw.columns if '위안' in col]]
        rev = rev.rename(columns={col: col[col.find('(') + 1:col.find(')')] for col in rev.columns})
        rev.index = pd.to_datetime(rev.index)
        return rev

    @property
    def interest_rate(self) -> pd.DataFrame:
        """
        국내 금리
        """
        cols = {
            "자금조정 예금금리"     : "예금금리",
            "자금조정 대출금리"     : "대출금리",
            "한국은행 기준금리"     : "기준금리",
            "콜금리(1일, 전체거래)" : "콜금리1D",
            "CD(91일)"              : "CD금리91D",
            "CP(91일)"              : "CP금리91D",
            "국고채(2년)"           : "국고채2Y",
            "국고채(3년)"           : "국고채3Y",
            "국고채(5년)"           : "국고채5Y",
            "국고채(10년)"          : "국고채10Y",
            "국고채(30년)"          : "국고채20Y",
            "회사채(3년, AA-)"      : "회사채3YAA-",
            "회사채(3년, BBB-)"     : "회사채3YBBB-",
        }
        raw = self.fetch(codes=['722Y001', '817Y002'])
        rev = raw[list(cols.keys())].rename(columns=cols)
        rev.index = pd.to_datetime(rev.index)
        return rev

    @property
    def nsi(self) -> pd.DataFrame:
        """
        뉴스심리지수[한국은행]
        한국은행은 경제분야 뉴스기사에 나타난 경제심리를 지수화한 뉴스심리지수(NSI)를 ECOS에 실험적으로 공개

        - 포털사이트의 경제분야 뉴스기사를 기반으로 표본문장을 추출
        - 각 문장에 나타난 긍정, 부정, 중립의 감성을 기계학습 방법으로 분류
        - 긍정과 부정 문장수의 차이를 계산하여 지수화한 지표

        * 지수 작성대상 표본은 ’05년 이후 50여개 언론사의 경제분야 뉴스기사 문장으로,
          일별 10,000개의 표본문장을 무작위로 추출하였음.

        * ’05.1.1~’22.1.31일중 일별 뉴스심리지수를 작성한 결과,
          장기평균치 100을 기준으로 대체로 대칭적인 흐름을 보이는 가운데 경제심리의 변화를 신속하게 포착됨.
        """
        raw = self.fetch(codes='521Y001')
        raw.index = pd.to_datetime(raw.index)
        return raw

    @property
    def bca(self) -> pd.DataFrame:
        """
        경상 수지 Balance On Current Account
        경상수지가 흑자라는 것은 상품과 서비스 등의 수출과 관련해 늘어나는 생산과 일자리가 수입으로 인해 줄어드는 것보다
        크다는 것을 의미한다. 때문에 그만큼 국민의 소득 수준이 높아지고 고용이 확대되는 긍정적인 효과가 있다.

        반대로 경상수지가 적자를 나타내는 경우 소득 수준이 낮아지고 실업이 늘어남과 동시에 외채가 늘어나면서 대외신인도가
        하락하게 된다. 나아가 국내외 여건 악화로 자본유입이 급격히 둔화되거나 대규모 자본유출이 나타날 경우 외화 유동성
        부족으로 외환위기에 이르게 될 가능성이 높아진다.
        """
        raw = self.fetch(codes='301Y017')
        rev = raw['경상수지']
        rev.index = pd.to_datetime(rev.index)
        return rev



if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    fetch = fetch()
    print(fetch.ecos_symbols)
    # print(fetch.ecos(['722Y001', '817Y002']))
