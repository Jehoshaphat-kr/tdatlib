from datetime import datetime, timedelta
from pytz import timezone
from tdatlib.toolbox import data
import pandas as pd


class _fetch(object):
    __k = "CEW3KQU603E6GA8VX0O9"
    __t = datetime.now(timezone('Asia/Seoul')).date()
    __p = 20

    @property
    def period(self) -> int:
        return self.__p

    @period.setter
    def period(self, period: int):
        self.__p = period
        return

    @property
    def symbols(self) -> pd.DataFrame:
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
            url = f"http://ecos.bok.or.kr/api/StatisticTableList/{self.__k}/xml/kr/1/10000/"
            df = data.xml_to_df(url=url)
            df = df[df.SRCH_YN == 'Y'].copy()
            df['STAT_NAME'] = df.STAT_NAME.apply(lambda x: x[x.find(' ') + 1:])
            df = df.drop(columns='SRCH_YN')
            df = df.rename(columns={'STAT_CODE': '코드', 'STAT_NAME': '지표명', 'CYCLE': '주기', 'ORG_NAME': '발행처'})
            self.__setattr__('__codes', df)
        return self.__getattribute__('__codes')

    def contains(self, symbol: str):
        """
        Single ECOS symbol containing label list
        :param symbol: symbol

                                     이름 주기      시점      종점  개수
        0           콜금리(1일, 전체거래)    D  19950103  20221005  7081
        1       콜금리(1일, 중개회사거래)    D  19960103  20221005  6785
        2                     국고채(5년)    D  20000104  20221005  5642
        ...                           ...  ...
        23  콜금리(1일, 은행증권금융차입)    D  20211125  20221005   213
        24                  통안증권(1년)    D  19950103  20221005  7042
        25                   국고채(50년)    D  20161011  20221005  1479
        """
        if not hasattr(self, f'__{symbol}_contains'):
            columns = dict(
                ITEM_NAME='이름',
                ITEM_CODE='코드',
                CYCLE='주기',
                START_TIME='시점',
                END_TIME='종점',
                DATA_CNT='개수'
            )
            url = f"http://ecos.bok.or.kr/api/StatisticItemList/{self.__k}/xml/kr/1/10000/{symbol}"
            self.__setattr__(f'__{symbol}_contains', data.xml_to_df(url=url)[columns.keys()].rename(columns=columns))
        return self.__getattribute__(f'__{symbol}_contains')

    def load(self, symbol:str, label:str) -> pd.Series:
        contained = self.contains(symbol=symbol)
        key = contained[contained.이름 == label]
        if key.empty:
            raise KeyError(f'{label} not found in {contained.이름}')
        if len(key) > 1:
            cnt = key['개수'].astype(int).max()
            key = key[key.개수 == str(cnt)]

        if not hasattr(self, f'__{symbol}_{label}_{self.__p}'):
            name, code, c, s, e, _ = tuple(key.values[0])
            url = f'http://ecos.bok.or.kr/api/StatisticSearch/{self.__k}/xml/kr/1/100000/{symbol}/{c}/{s}/{e}/{code}'
            tseries = data.xml_to_df(url=url)[['TIME', 'DATA_VALUE']]
            tseries['TIME'] = pd.to_datetime(tseries['TIME'] + ('01' if c == 'M' else '1231' if c == 'Y' else ''))
            tseries.set_index(keys='TIME', inplace=True)
            tseries.name = name
            if c == 'M':
                tseries.index = tseries.index.to_period('M').to_timestamp('M')
            self.__setattr__(
                f'__{symbol}_{label}_{self.__p}',
                tseries[tseries.index >= (self.__t - timedelta(self.__p * 365)).strftime("%Y-%m-%d")].astype(float)
            )
        return self.__getattribute__(f'__{symbol}_{label}_{self.__p}')


class ecos(_fetch):

    @property
    def props(self) -> list:
        return [e for e in self.__dir__() if not e.startswith('_') and not (e[0].isalpha() and e[0].islower())]

    @property
    def 기준금리(self) -> pd.Series:
        return self.load('722Y001', '한국은행 기준금리')

    @property
    def 국고채1Y(self) -> pd.Series:
        return self.load('817Y002', '국고채(1년)')

    @property
    def 국고채2Y(self) -> pd.Series:
        return self.load('817Y002', '국고채(2년)')

    @property
    def 국고채3Y(self) -> pd.Series:
        return self.load('817Y002', '국고채(3년)')

    @property
    def 국고채5Y(self) -> pd.Series:
        return self.load('817Y002', '국고채(5년)')

    @property
    def 국고채10Y(self) -> pd.Series:
        return self.load('817Y002', '국고채(10년)')

    @property
    def CD금리91D(self) -> pd.Series:
        return self.load('817Y002', 'CD(91일)')

    @property
    def CP금리91D(self) -> pd.Series:
        return self.load('817Y002', 'CP(91일)')

    @property
    def 회사채3YAA(self) -> pd.Series:
        return self.load('817Y002', '회사채(3년, AA-)')

    @property
    def 회사채3YBBB(self) -> pd.Series:
        return self.load('817Y002', '회사채(3년, BBB-)')

    @property
    def 원달러환율(self) -> pd.DataFrame:
        return pd.concat(
            objs=dict(
                시가=self.load('731Y003', '원/달러(시가)'),
                고가=self.load('731Y003', '원/달러(고가)'),
                저가=self.load('731Y003', '원/달러(저가)'),
                종가=self.load('731Y003', '원/달러(종가)')
            ), axis=1
        )

    @property
    def 원위안환율(self) -> pd.DataFrame:
        return pd.concat(
            objs=dict(
                시가=self.load('731Y003', '원/위안(시가)'),
                고가=self.load('731Y003', '원/위안(고가)'),
                저가=self.load('731Y003', '원/위안(저가)'),
                종가=self.load('731Y003', '원/위안(종가)')
            ), axis=1
        )



if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    app = ecos()
    app.period = 15

    print(app.props)
    # print(app.load('817Y002', '국고채(3년)'))
    print(app.load('121Y013', '총수신(요구불예금 및 수시입출식 저축성예금 포함)'))
    # print(app.contains('722Y001'))
    # print(app.기준금리)
    # print(app.원달러환율)