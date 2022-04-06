from tdatlib.fetch.market.krx import *


class kr_market:
    __local = False
    __date, __wics, __wi26, __thm = str(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __etf_g, __etf_s = pd.DataFrame(), pd.DataFrame()
    __perf, __icm, __depo, __disp = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    def set_local(self):
        self.__local = True
        return

    @property
    def wise_date(self) -> str:
        if not self.__date:
            self.__date = getWiseDate()
        return self.__date

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
            return self.__icm.drop(columns=['날짜'])

        today = krx.get_nearest_business_day_in_a_week(date=kst.strftime("%Y%m%d"))
        self.__icm = pd.read_csv(archive.icm, index_col='종목코드', encoding='utf-8')
        self.__icm.index = self.__icm.index.astype(str).str.zfill(6)

        icm_date = str(self.__icm['날짜'][0])
        is_ongoing = icm_date == today and 830 < int(kst.strftime("%H%M")) <= 1530
        if not icm_date == today or is_ongoing:
            self.__icm = pd.concat(
                objs=[
                    getCorpIPO(),
                    krx.get_market_cap_by_ticker(date=today, market="ALL"),
                    krx.get_market_fundamental(date=today, market='ALL')
                ], axis=1
            )
            self.__icm['날짜'] = icm_date if is_ongoing else today
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
            return self.__wi26.drop(columns=['날짜'])

        self.__wi26 = pd.read_csv(archive.wi26, index_col='종목코드', encoding='utf-8')
        self.__wi26.index = self.__wi26.index.astype(str).str.zfill(6)
        if not str(self.__wi26['날짜'][0]) == self.wise_date:
            self.__wi26 = getWiseGroup(name='WI26', date=self.wise_date)
            self.__wi26.to_csv(archive.wi26, index=True, encoding='utf-8')
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
            return self.__wics.drop(columns=['날짜'])

        self.__wics = pd.read_csv(archive.wics, index_col='종목코드', encoding='utf-8')
        self.__wics.index = self.__wics.index.astype(str).str.zfill(6)
        if not str(self.__wics['날짜'][0]) == self.wise_date:
            self.__wics = getWiseGroup(name='WICS', date=self.wise_date)
            self.__wics.to_csv(archive.wics, index=True, encoding='utf-8')
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
    def etf_group(self) -> pd.DataFrame:
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

        if self.__etf_g.empty:
            self.__etf_g = getEtfGroup()
        return self.__etf_g

    @property
    def etf_stat(self) -> pd.DataFrame:
        """
                                     종목명   종가        시가총액
        종목코드
        069500                    KODEX 200  39725  5718400000000
        371460  TIGER 차이나전기차SOLACTIVE  16435  3229800000000
        278540          KODEX MSCI Korea TR  12820  2239700000000
        ...                             ...    ...            ...
        334700   KBSTAR 팔라듐선물인버스(H)   5520     1700000000
        287310         KBSTAR 200경기소비재  10895     1500000000
        287320             KBSTAR 200산업재  11135     1300000000
        """
        if self.__etf_s.empty:
            self.__etf_s = getEtfList()
        return self.__etf_s

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

    @property
    def i_display(self) -> pd.DataFrame:
        """
        KOSPI코드        KOSPI지수  KOSDAQ코드     KOSDAQ지수  KRX코드     KRX지수 THEME코드           THEME지수
             1001           코스피        2001         코스닥     5042     KRX 100      1163    코스피 고배당 50
             1002    코스피 대형주        2002  코스닥 대형주     5043  KRX 자동차      1164  코스피 배당성장 50
             1003    코스피 중형주        2003  코스닥 중형주     5044  KRX 반도체      1165   코스피 우선주 지수
              ...              ...         ...            ...       ...         ...       ...                 ...
        """
        if not self.__disp.empty:
            return self.__disp

        objs = []
        process = tqdm(['KOSPI', 'KOSDAQ', 'KRX', 'THEME'])
        for market in process:
            process.set_description(desc=f'{market} 지수 종목 수집 중...')
            data = getIndexGroup(market=market)
            obj = data.rename(columns={'종목명': f'{market}지수'}).drop(columns=['지수분류'])
            obj.index.name = f'{market}코드'
            objs.append(obj.reset_index(level=0))
        self.__disp = pd.concat(objs=objs, axis=1).fillna('-')
        return self.__disp


if __name__ == "__main__":
    market = market_krx()
    print(market.wics)
    print(market.wi26)