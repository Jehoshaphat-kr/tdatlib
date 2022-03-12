from raw import *


class interface:
    __local = False
    __wics, __wi26, __thm, __etf = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __perf, __icm = pd.DataFrame(), pd.DataFrame()
    def __init__(self):
        self.__date = getWiseDate()
        return

    def set_local(self):
        self.__local = True
        return

    @property
    def icm(self) -> pd.DataFrame:
        """
        IPO, Market Cap and Multiples: 상장일, 시가총액 및 투자배수(기초) 정보
                 종목명         IPO   종가       시가총액   거래량    거래대금  상장주식수    BPS    PER   PBR    EPS   DIV   DPS
        종목코드
        000210       DL  1976-02-02  57100  1196580976400    56637  3230631400    20955884  67178   4.37  0.85  13077  2.28  1300
        004840  DRB동일  1976-05-21   4970    99052100000     4725    23512045    19930000  17702  41.06  0.28    121  1.01    50
        155660      DSR  2013-05-15   5560    88960000000   154220   874995590    16000000  10087   9.96  0.55    558  0.90    50
        ...         ...         ...    ...            ...      ...         ...         ...    ...    ...   ...    ...   ...   ...
        000547      NaN         NaN  27800     4270080000      231     6440750      153600      0   0.00  0.00      0  0.00     0
        009275      NaN         NaN  36500     3312010000      215     7855350       90740      0   0.00  0.00      0  0.00     0
        001529      NaN         NaN  34650     3108867300    12358   437491300       89722      0   0.00  0.00      0  0.43   150
        """
        if not self.__icm.empty:
            return self.__icm

        today = kst.strftime("%Y%m%d")
        self.__icm = pd.read_csv(archive.icm, index_col='종목코드', encoding='utf-8')
        self.__icm.index = self.__icm.index.astype(str).str.zfill(6)
        is_latest = str(self.__icm['날짜'][0]) == today
        is_ongoing = is_latest and int(kst.strftime("%H%M")) <= 1530
        if not is_latest or is_ongoing:
            self.__icm = pd.concat(
                objs=[
                    getCorpIPO(),
                    krx.get_market_cap_by_ticker(date=today, market="ALL", prev=True),
                    krx.get_market_fundamental(date=today, market='ALL', prev=True)
                ], axis=1
            )
            self.__icm['날짜'] = today
            self.__icm.index.name = '종목코드'
            self.__icm.to_csv(archive.icm, index=True, encoding='utf-8')
        return self.__icm.drop(columns=['날짜'])


    @property
    def wi26(self) -> pd.DataFrame:
        """
                           종목명     섹터
        종목코드
        096770       SK이노베이션   에너지
        010950              S-Oil   에너지
        267250     현대중공업지주   에너지
        ...                  ...       ...
        003480  한진중공업홀딩스  유틸리티
        053050          지에스이  유틸리티
        034590      인천도시가스  유틸리티
        """
        if not self.__wi26.empty:
            return self.__wi26

        self.__wi26 = pd.read_csv(archive.wi26, index_col='종목코드', encoding='utf-8')
        self.__wi26.index = self.__wi26.index.astype(str).str.zfill(6)
        if not str(self.__wi26['날짜'][0]) == self.__date:
            self.__wi26 = getWiseGroup(name='WI26', date=self.__date)
            self.__wi26['날짜'] = self.__date
            self.__wi26.to_csv(archive.wi26, index=False, encoding='utf-8')
            self.__wi26.set_index(keys='종목코드', inplace=True)
        return self.__wi26.drop(columns=['날짜'])

    @property
    def wics(self) -> pd.DataFrame:
        """
                          종목명      산업      섹터
        종목코드
        096770      SK이노베이션    에너지    에너지
        010950             S-Oil    에너지    에너지
        267250    현대중공업지주    에너지    에너지
        ...                  ...       ...       ...
        003480  한진중공업홀딩스  유틸리티  유틸리티
        053050          지에스이  유틸리티  유틸리티
        034590      인천도시가스  유틸리티  유틸리티
        """
        if not self.__wics.empty:
            return self.__wics

        self.__wics = pd.read_csv(archive.wics, index_col='종목코드', encoding='utf-8')
        self.__wics.index = self.__wics.index.astype(str).str.zfill(6)
        if not str(self.__wics['날짜'][0]) == self.__date:
            self.__wics = getWiseGroup(name='WICS', date=self.__date)
            self.__wics['날짜'] = self.__date
            self.__wics.to_csv(archive.wics, index=False, encoding='utf-8')
            self.__wics.set_index(keys='종목코드', inplace=True)
        return self.__wics.drop(columns=['날짜'])

    @property
    def theme(self) -> pd.DataFrame:
        """
                     종목명          섹터
        종목코드
        211270       AP위성      우주항공
        138930  BNK금융지주          배당
        079160       CJ CGV  미디어컨텐츠
        ...             ...           ...
        298000     효성화학        수소차
        093370         후성       2차전지
        145020         휴젤        바이오
        """
        if self.__thm.empty:
            self.__thm = getThemeGroup()
        return self.__thm

    @property
    def etf(self) -> pd.DataFrame:
        """
                                          종목명          산업   섹터
        종목코드
        069500                         KODEX 200  국내 시장지수  대형
        278540               KODEX MSCI Korea TR  국내 시장지수  대형
        278530                       KODEX 200TR  국내 시장지수  대형
        ...                                  ...            ...   ...
        396520         TIGER 차이나반도체FACTSET           해외  중국
        391600    KINDEX 미국친환경그린테마INDXX           해외  미국
        391590         KINDEX 미국스팩&IPO INDXX           해외  미국
        """
        if self.__local:
            checkEtfLatest()

        if self.__etf.empty:
            self.__etf = getEtfGroup()
        return self.__etf

    @property
    def performance(self) -> pd.DataFrame:
        """
                 R1D   R1W    R1M    R3M    R6M    R1Y
        종목코드
        095570  0.35  0.18  10.31   6.18  -4.87  41.75
        006840  3.39  1.91   7.29   2.64 -21.36 -25.61
        054620  1.26 -0.82   7.11  -8.02 -34.33  56.29
        ...      ...   ...    ...    ...    ...    ...
        176710  0.00 -0.31   0.05  -0.95  -1.43  -2.35
        140950 -0.81 -2.39  -3.89 -10.23 -12.29 -15.21
        419890  0.04  0.04    NaN    NaN    NaN    NaN
        """
        if not self.__perf.empty:
            return self.__perf

        if os.path.isfile(archive.performance):
            self.__perf = pd.read_csv(archive.performance, encoding='utf-8', index_col='종목코드')
            self.__perf.index = self.__perf.index.astype(str).str.zfill(6)
            return self.__perf

        self.__perf = pd.concat(objs=[getCorpPerformance(), getEtfPerformance()], axis=0, ignore_index=False)
        self.__perf.to_csv(archive.performance, encoding='utf-8', index=True)
        return self.__perf

if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    api = interface()
    print(api.icm)
    print(api.wi26)
    print(api.wics)
    print(api.theme)
    print(api.etf)
    print(api.performance)