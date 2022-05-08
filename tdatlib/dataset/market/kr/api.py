from tdatlib.dataset.market.kr.common.icm import calc_icm
from tdatlib.dataset.market.kr.common.wise import (
    fetch_wics,
    fetch_wi26,
    read_theme
)
from tdatlib.dataset.market.kr.common.etf import (
    fetch_etf_list,
    read_etf_group
)
from tdatlib.dataset.market.kr.common.rtrn import fetch_returns
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


class kr(object):

    def __init__(self, td:str=str()):
        _now = datetime.now(timezone('Asia/Seoul'))
        _lat = get_nearest_business_day_in_a_week(date=_now.strftime("%Y%m%d"))
        self.trading_date = td if td else _lat

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

    def get_deposit(self, label:str):
        if not hasattr(self, f'__{label}'):
            self.__setattr__(f'__{label}', get_index_portfolio_deposit_file(CD_INDEX[label.lower()]))
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


if __name__ == '__main__':
    market = kr()
    print(market.icm)
    print(market.wi26)
    print(market.wics)
    print(market.theme)
    print(market.etf_group)
    print(market.etf_list)
    print(market.get_returns(tickers=market.theme.index))

    market2 = kr(td='20210428')
    print(market2.get_returns(tickers=market2.theme.index))
