from tdatlib.fetch.market._krx import krx
from inspect import currentframe as inner
import pandas as pd


class market_kr(krx):

    def __init__(self):
        super().__init__()
        return

    def __checkattr__(self, name:str) -> str:
        if not hasattr(self, f'__{name}'):
            _func = self.__getattribute__(f'_get_{name}')
            self.__setattr__(f'__{name}', _func())
        return f'__{name}'

    @property
    def icm(self) -> pd.DataFrame:
        """
        IPO, Market Cap and Multiples: 상장일, 시가총액 및 투자배수(기초) 정보

                 종목명         IPO   종가       시가총액  ...    BPS    PER   PBR    EPS   DIV   DPS
        종목코드
        000210       DL  1976-02-02  57100  1196580976400  ...  67178   4.37  0.85  13077  2.28  1300
        004840  DRB동일  1976-05-21   4970    99052100000  ...  17702  41.06  0.28    121  1.01    50
        155660      DSR  2013-05-15   5560    88960000000  ...  10087   9.96  0.55    558  0.90    50
        ...         ...         ...    ...            ...  ...    ...   ...    ...   ...   ...
        000547      NaN         NaN  27800     4270080000  ...      0   0.00  0.00      0  0.00     0
        009275      NaN         NaN  36500     3312010000  ...      0   0.00  0.00      0  0.00     0
        001529      NaN         NaN  34650     3108867300  ...      0   0.00  0.00      0  0.43   150
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))


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
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

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
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

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
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

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
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def etfs(self) -> pd.DataFrame:
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
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def raw_perf(self) -> pd.DataFrame:
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
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def indices(self) -> pd.DataFrame:
        """
        디스플레이용 시장 지수 종류
        KOSPI코드        KOSPI지수  KOSDAQ코드     KOSDAQ지수  KRX코드     KRX지수 THEME코드           THEME지수
             1001           코스피        2001         코스닥     5042     KRX 100      1163    코스피 고배당 50
             1002    코스피 대형주        2002  코스닥 대형주     5043  KRX 자동차      1164  코스피 배당성장 50
             1003    코스피 중형주        2003  코스닥 중형주     5044  KRX 반도체      1165   코스피 우선주 지수
              ...              ...         ...            ...       ...         ...       ...                 ...
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    def get_related(self, ticker:str) -> list:
        """
        업종 연관도 상위 시가총액 6종목 선출
        :return:
        ['000660', '402340', '000990', '058470', '005290', '357780']
        """
        wics = self.wics.copy()
        if not ticker in wics.index:
            raise KeyError(f"산업 분류에 없는 종목 코드 {ticker} 입니다")
        rel = wics[wics['섹터'] == str(wics.loc[ticker, '섹터'])].copy()
        rel = rel.join(self.icm['시가총액'], how='left').sort_values(by='시가총액', ascending=False).drop(index=[ticker])
        return rel.index.tolist()[:6]


if __name__ == "__main__":
    # pd.set_option('display.expand_frame_repr', False)

    market = market_kr()
    # print(market.icm)
    # print(market.wics)
    # print(market.wi26)
    # print(market.theme)
    # print(market.etf_group)
    # print(market.etfs)
    print(market.raw_perf)
    # print(market.indices)