from pandas_datareader import get_data_fred as fred
from datetime import datetime, timedelta
from tdatlib import toolbox
import pandas as pd


class fetch(object):

    KEY = "CEW3KQU603E6GA8VX0O9"

    # 금리
    US기준금리            = 'EFFR'
    US실질금리            = 'FEDFUNDS'
    US10년물금리          = 'T10YFF'
    US장단기금리차10Y2Y   = 'T10Y2Y'
    US30년만기모기지금리  = 'MORTGAGE30US'

    # 물가 / 인플레이션
    US5년기대인플레       = 'T5YIFR'
    US소비자물가지수      = 'CPIAUCSL'
    US10년평형인플레      = 'T10YIE'

    # 유가
    BRENT유가             = 'DCOILBRENTEU'
    WTI유가               = 'DCOILWTICO'
    CRUDE유가변동성       = 'OVXCLS'


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


if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    fetch = fetch()
