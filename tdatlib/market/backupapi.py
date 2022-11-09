from tdatlib.market.icm import calc_icm
from tdatlib.market.etf import (
    fetch_etf_list,
    read_etf_group,
    isetfokay
)
from tdatlib.market.wise import (
    fetch_wics,
    fetch_wi26,
    read_theme
)
# from tdatlib.dataset.market.kr.treemap import (
#     treemap,
#     treemap_deploy
# )
from pykrx.stock import (
    get_nearest_business_day_in_a_week,
    get_index_portfolio_deposit_file
)
from pytz import timezone
from datetime import datetime
import pandas as pd


CD_INDEX = {
    'kospi'     : '1001',
    'kospi200'  : '1028',
    'kospimid'  : '1003',
    'kospismall': '1004',
    'kosdaq'    : '2001',
    'kosdaq150' : '2203',
    'kosdaqMID' : '2003',
}


class _krse(object):

    def __init__(self, td:str=str()):
        _now = datetime.now(timezone('Asia/Seoul'))
        _lat = get_nearest_business_day_in_a_week(date=_now.strftime("%Y%m%d"))
        self.trading_date = td if td else _lat
        self.is_test_mode = True if td else False

        self.__is_market_on = 859 < int(_now.strftime("%H%M")) < 1531 and _now.strftime("%Y%m%d") == self.trading_date
        self.__write_ok     = _lat == self.trading_date
        return

    @property
    def icm(self) -> pd.DataFrame:
        """
        IPO, Market Cap and Multiples: 상장일, 시가총액 및 투자배수(기초) 정보
        :return:

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
        if not hasattr(self, '__icm'):
            self.__setattr__(
                '__icm',
                calc_icm(
                    trading_date=self.trading_date,
                    is_market_open=self.__is_market_on,
                    write_ok=self.__write_ok
                )
            )
        return self.__getattribute__('__icm')

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
        if not hasattr(self, '__wi26'):
            self.__setattr__('__wi26', fetch_wi26())
        return self.__getattribute__('__wi26')

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
        if not hasattr(self, '__wics'):
            self.__setattr__('__wics', fetch_wics())
        return self.__getattribute__('__wics')

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
        return read_theme()

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
        return read_etf_group()

    @property
    def etf_list(self) -> pd.DataFrame:
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
        return fetch_etf_list()

    def get_deposit(self, label:str) -> list:
        ticker = label if label.isdigit() else CD_INDEX[label.lower()]
        if not hasattr(self, f'__{label}'):
            self.__setattr__(f'__{label}', get_index_portfolio_deposit_file(ticker))
        return self.__getattribute__(f'__{label}')

    def get_returns(self, tickers) -> pd.DataFrame:
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
        return fetch_returns(
            td=self.trading_date, tickers=tickers, is_market_open=self.__is_market_on, write_ok=self.__write_ok
        )

    def treemap(self, category:str, sub_category:str=str()):
        """
        시장 지도 데이터프레임
        :return:

                          종목코드        종목명    분류  ...     CPER     CDIV            ID
        0                   096770  SK이노베이션  에너지  ...  #F63538  #8B444E  SK이노베이션
        1                   010950         S-Oil  에너지  ...  #35764E  #2F9E4F         S-Oil
        2                   267250        HD현대  에너지  ...  #F63538  #30CC5A        HD현대
        ..                     ...           ...     ...  ...      ...      ...           ...
        716  화장품,의류_WI26_전체   화장품,의류    전체  ...  #8B444E  #414554   화장품,의류
        717         화학_WI26_전체          화학    전체  ...  #8B444E  #414554          화학
        718              WI26_전체          전체          ...  #C8C8C8  #C8C8C8          전체
        """
        if not hasattr(self, f'__treemap_{category}_{sub_category}'):
            self.__setattr__(
                f'__treemap_{category}_{sub_category}',
                treemap(market=self, category=category, sub_category=sub_category)
            )
        return self.__getattribute__(f'__treemap_{category}_{sub_category}').mapframe

    def sectors(self, category:str, sub_category:str=str()):
        """
        시장 지도 섹터별
        :return:

                          종목코드       종목명  분류  IPO  ...     CPBR     CPER     CDIV           ID
        692       IT가전_WI26_전체       IT가전  전체  NaN  ...  #F63538  #F63538  #F63538       IT가전
        693   IT하드웨어_WI26_전체   IT하드웨어  전체  NaN  ...  #BF4045  #BF4045  #BF4045   IT하드웨어
        694     건강관리_WI26_전체     건강관리  전체  NaN  ...  #F63538  #F63538  #BF4045     건강관리
        ...                    ...          ...   ...  ...  ...      ...      ...      ...          ...
        715    호텔,레저_WI26_전체    호텔,레저  전체  NaN  ...  #BF4045  #F63538  #F63538    호텔,레저
        716  화장품,의류_WI26_전체  화장품,의류  전체  NaN  ...  #8B444E  #8B444E  #414554  화장품,의류
        717         화학_WI26_전체         화학  전체  NaN  ...  #8B444E  #8B444E  #414554         화학
        """
        if not hasattr(self, f'__treemap_{category}_{sub_category}'):
            self.__setattr__(
                f'__treemap_{category}_{sub_category}',
                treemap(market=self, category=category, sub_category=sub_category)
            )
        mapframe = self.__getattribute__(f'__treemap_{category}_{sub_category}').mapframe
        bars = self.__getattribute__(f'__treemap_{category}_{sub_category}').barframe
        return mapframe[mapframe.종목코드.isin(bars)]

    def treemap_deploy(self):
        """
        시장 지도 배포용 js 생성 '/dataset/archive/treemap/deploy/js'
        :return: 
        """
        treemap_deploy(market=self).to_js()
        return

    def isetfokay(self):
        """
        수기 ETF 관리 최신화 여부
        :return:
        """
        return isetfokay(curr=self.etf_list)


# Alias
krse = _krse()

if __name__ == '__main__':

    print(krse.icm)
    print(krse.wi26)
    print(krse.wics)
    print(krse.theme)
    print(krse.etf_group)
    print(krse.etf_list)
    # print(market.get_returns(tickers=market.theme.index))
    # print(krse.treemap(category='WI26'))
    # print(krse.sectors(category='WI26'))

    # market2 = KR(td='20210428')
    # print(market2.get_returns(tickers=market2.theme.index))
