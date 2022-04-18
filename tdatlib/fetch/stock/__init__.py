from tdatlib.fetch.stock.common import (
    fetch_currency,
    fetch_name,
    fetch_ohlcv,
    fetch_related
)

from tdatlib.fetch.stock.fnguide import (
    URL1, URL2,
    fetch_summary,
    fetch_products,
    fetch_statement,
    fetch_multifactor,
    fetch_benchmark_return,
    fetch_benchmark_multiple,
    fetch_consensus,
    fetch_foreign_rate,
    fetch_short_sell,
    fetch_short_balance,
    fetch_expenses,
    fetch_multiple_band,
    fetch_multiple_series,
    fetch_nps
)

from inspect import currentframe as inner
import pandas as pd


class fetch_stock(object):

    def __init__(self, ticker:str, name:str=str(), period:int=5):
        self.ticker = ticker
        self.__name = name
        self.period = period
        return

    def __attr__(self, p:str, fname:str=str(), **kwargs):
        if not hasattr(self, f'__{p}'):
            self.__setattr__(f'__{p}', globals()[f"fetch_{fname if fname else p}"](**kwargs))
        return self.__getattribute__(f'__{p}')

    def __page__(self, n:int=1) -> list:
        if not hasattr(self, f'__page{n}'):
            self.__setattr__(f'__page{n}', pd.read_html(globals()[f'URL{n}'] % self.ticker, encoding='utf-8'))
        return self.__getattribute__(f'__page{n}')

    @property
    def name(self) -> str:
        """
        종목명
        :return:
        """
        return self.__name if self.__name else self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def currency(self) -> str:
        """
        통화 단위
        :return: USD / KRW / - (For INDEX)
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def ohlcv(self) -> pd.DataFrame:
        """
        시가 / 고가 / 저가 / 종가 / 거래량
        :return:
                     시가   고가   저가   종가     거래량
        날짜
        2017-04-17  42000  42080  41520  41560    104495
        2017-04-18  41680  41820  41280  41500    137213
        2017-04-19  41299  41420  40900  40900    235258
        ...           ...    ...    ...    ...       ...
        2022-04-13  67300  69000  67200  68700  17378619
        2022-04-14  68700  68700  67500  67500  16409494
        2022-04-15  67200  67300  66500  66700   8569557
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker, period=self.period)

    @property
    def summary(self) -> str:
        """
        기업 개요 요약 다운로드
        :return:

        1983년 현대전자로 설립됐고, 2001년 하이닉스반도체를 거쳐 2012년 최대주주가 SK텔레콤으로 바뀌면서 ...
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def products(self) -> pd.Series:
        """
        매출 제품 구성
        :return:

        석유화학 사업부문    47.30
        전지 사업부문        41.74
        첨단소재 사업부문     7.51
        공통 및 기타부문      1.83
        기타(계)              1.62
        Name: 2021/12, dtype: float64
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def annual_stat(self) -> pd.DataFrame:
        """
        연간 재무 요약
        :return:

                      매출액  영업이익  영업이익(발표기준)  ...   PBR  발행주식수  배당수익률
        2017/12     256980.0   29285.0             29285.0  ...  1.92    70592.0         1.48
        2018/12     281830.0   22461.0             22461.0  ...  1.56    70592.0         1.73
        2019/12     273531.0    8254.0              8254.0  ...  1.43    70592.0         0.63
        2020/12     300589.0   18054.0             18054.0  ...  3.57    70592.0         1.21
        2021/12     426547.0   50255.0             50255.0  ...  2.22    70592.0         1.95
        2022/12(E)  478768.0   36603.0                 NaN  ...  1.55        NaN          NaN
        2023/12(E)  544645.0   45917.0                 NaN  ...  1.43        NaN          NaN
        2024/12(E)  588064.0   47563.0                 NaN  ...  1.18        NaN          NaN
        """
        return self.__attr__('annual', 'statement', htmls=self.__page__(1), kind='annual')

    @property
    def quarter_stat(self) -> pd.DataFrame:
        """
        연간 재무 요약
        :return:

                      매출액  영업이익  영업이익(발표기준)  당기순이익  ...  PER   PBR  발행주식수  배당수익률
        2020/12      88914.0    1238.0              1238.0     -3434.0  ...  NaN  3.57     70592.0        1.21
        2021/03      96500.0   14081.0             14081.0     13710.0  ...  NaN  3.35     70592.0         NaN
        2021/06     114561.0   21398.0             21398.0     15663.0  ...  NaN  3.26     70592.0         NaN
        2021/09     106102.0    7266.0              7266.0      6799.0  ...  NaN  2.85     70592.0         NaN
        2021/12     109384.0    7509.0              7509.0      3368.0  ...  NaN  2.22     70592.0        1.95
        2022/03(E)  112858.0    8776.0                 NaN      6640.0  ...  NaN   NaN         NaN         NaN
        2022/06(E)  119462.0    8250.0                 NaN      5810.0  ...  NaN   NaN         NaN         NaN
        2022/09(E)  123494.0    9376.0                 NaN      6341.0  ...  NaN   NaN         NaN         NaN
        """
        return self.__attr__('quarter', 'statement', htmls=self.__page__(1), kind='quarter')

    @property
    def multifactor(self) -> pd.DataFrame:
        """
        멀티 팩터
        :return:

                         LG화학  소재(업종)
        팩터
        베타               0.08       0.03
        배당성             0.95      -0.28
        수익건전성         0.36      -0.28
        성장성             0.46      -0.50
        기업투자          -0.59      -0.24
        거시경제 민감도    0.18       0.05
        모멘텀            -1.65       0.18
        단기 Return        1.34       0.20
        기업규모           0.80      -2.23
        거래도            -0.11       0.67
        밸류              -0.08       0.09
        변동성             0.62       0.50
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def benchmark_return(self) -> pd.DataFrame:
        """
        벤치마크 대비 수익률
        :return:

                                     (Daily) 3M                    (Weekly) 1Y
                     LG화학  코스피 화학  KOSPI    LG화학  코스피 화학   KOSPI
        TRD_DT
        2021-04-16     NaN           NaN    NaN   100.00        100.00  100.00
        2021-04-23     NaN           NaN    NaN    97.73         99.92   99.76
        2021-04-30     NaN           NaN    NaN   101.38        101.78   99.65
        ...            ...           ...    ...      ...           ...     ...
        2022-04-13   73.27         89.94  93.99      NaN           NaN     NaN
        2022-04-14   72.70         90.36  94.00      NaN           NaN     NaN
        2022-04-15   71.43         89.59  93.29    56.90         74.05   84.34
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def benchmark_multiple(self) -> pd.DataFrame:
        """
        벤치마크 대비 투자배수
        :return:

                                       PER                     EV/EBITDA                           ROE
               LG화학  코스피 화학  코스피   LG화학  코스피 화학  코스피   LG화학  코스피 화학  코스피
        2020   125.83       110.28   22.35    16.55        15.02    8.59     2.93         1.36    5.27
        2021    13.12        11.58   11.07     7.37         7.31    6.83    18.47        11.61   10.85
        2022E   16.95        10.90   11.18     6.60         5.53    5.55     9.88        11.00   10.03
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def consensus(self) -> pd.DataFrame:
        """
        투자 의견
        :return:
                투자의견  목표주가    종가
        날짜
        2021-04-16  4.00   1240000  897000
        2021-04-19  4.00   1240000  881000
        2021-04-20  4.00   1240000  893000
        ...          ...       ...     ...
        2022-04-13  4.00    838235  518000
        2022-04-14  4.00    838235  514000
        2022-04-15  4.00    834375  505000
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def foreign_rate(self) -> pd.DataFrame:
        """
        외국인 소진율
        :return:

                                (Daily) 3M           (Weekly) 1Y            (Monthly) 3Y
                      종가  외국인보유비중   종가  외국인보유비중   종가  외국인보유비중
        날짜
        2019-04-01     NaN            NaN     NaN            NaN  366591             39
        2019-05-01     NaN            NaN     NaN            NaN  337071          38.78
        2019-06-01     NaN            NaN     NaN            NaN  344184          38.65
        ...            ...            ...     ...            ...     ...            ...
        2022-04-13  518000          48.59     NaN            NaN     NaN            NaN
        2022-04-14  514000          48.60     NaN            NaN     NaN            NaN
        2022-04-15  505000          48.64  510400          48.59     NaN            NaN
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def short_sell(self) -> pd.DataFrame:
        """
        공매도 비율
        :return:

                   차입공매도비중  수정 종가
        날짜
        2021-04-19          0.03      881000
        2021-04-26          0.10      883000
        2021-05-03          1.01      907000
        ...                  ...         ...
        2022-03-28          3.13      523000
        2022-04-04          3.16      526000
        2022-04-11          6.38      510000
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def short_balance(self) -> pd.DataFrame:
        """
        대차 잔고 비율
        :return:

                   대차잔고비중  수정 종가
        날짜
        2021-04-19        4.62      881000
        2021-04-26        4.70      883000
        2021-05-03        4.59      907000
        ...                ...         ...
        2022-03-28        5.18      523000
        2022-04-04        4.90      526000
        2022-04-11        4.78      510000
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def expenses(self) -> pd.DataFrame:
        """
        주요 비용
        :return:

                 판관비율  매출원가율  R&D투자비중  무형자산처리비중  당기비용처리비중
        2016/12       NaN         NaN         3.28              0.00              3.28
        2017/12       NaN         NaN         3.49              0.08              3.41
        2018/12     11.00       81.03         3.78              0.10              3.69
        2019/12     14.11       82.87         3.95              0.06              3.89
        2020/12     15.01       78.98         3.79              0.00              3.80
        2021/12     14.52       73.70          NaN               NaN               NaN
        """
        return self.__attr__(inner().f_code.co_name, htmls=self.__page__(2))

    @property
    def nps(self):
        """
        EPS, BPS, EBITA(PS), DPS
        :return:

                      EPS        BPS   EBITDAPS  보통주DPS
        날짜
        2018/12  18811.78  222761.04   47691.42     6000.0
        2019/12   4003.07  221763.78   34259.62     2000.0
        2020/12   6548.63  230896.22   52583.77    10000.0
        2021/12  46879.58  277356.64  100488.75    12000.0
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def multiple_band(self) -> (pd.DataFrame, pd.DataFrame):
        """
        PER / PBR 밴드
        :return:

        (             수정주가     13.12X      42.14X      71.16X     100.17X     129.19X  <- PER BAND
            날짜
            2017-12-01  405000  326080.94  1047274.05  1768467.16  2489660.27  3210853.38
            2018-01-01  432000  319475.07  1026057.99  1732640.91  2439223.83  3145806.75
            2018-02-01  383000  312869.21  1004841.94  1696814.67   2388787.4  3080760.13
            ...            ...        ...         ...         ...         ...         ...
            2024-10-01     NaN  517257.86  1661276.91  2805295.96     3949315  5093334.05
            2024-11-01     NaN  519936.89  1669881.14  2819825.39  3969769.64   5119713.9
            2024-12-01     NaN  522615.91  1678485.37  2834354.83  3990224.28  5146093.74
            (and)
                      수정주가      1.00X      1.68X       2.36X       3.03X       3.71X  <- PBR BAND
            날짜
            2017-12-01  405000  211078.57  354084.30   497090.03   640095.76   783101.49
            2018-01-01  432000  212052.11  355717.41   499382.72   643048.02   786713.33
            2018-02-01  383000  213025.65  357350.53   501675.40   646000.28   790325.16
            ...            ...        ...        ...         ...         ...         ...
            2024-10-01     NaN  414279.74  694954.26   975628.78  1256303.30  1536977.82
            2024-11-01     NaN  420478.67  705352.97   990227.27  1275101.57  1559975.87
            2024-12-01     NaN  426677.61  715751.69  1004825.77  1293899.85  1582973.93
        )
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)

    @property
    def multiple_series(self) -> pd.DataFrame:
        """
        투자 배수 시계열
        :return:

                       BPS    PER   PBR    EPS   DIV    DPS
        날짜
        2019-04-17  206544  14.63  1.80  25367  1.62   6000
        2019-04-18  206544  14.55  1.79  25367  1.63   6000
        2019-04-19  206544  14.45  1.77  25367  1.64   6000
        ...            ...    ...   ...    ...   ...    ...
        2022-04-13  230440  77.71  2.25   6666  1.93  10000
        2022-04-14  230440  77.11  2.23   6666  1.95  10000
        2022-04-15  230440  75.76  2.19   6666  1.98  10000
        """
        return self.__attr__(inner().f_code.co_name, ticker=self.ticker)


if __name__ == "__main__":
    t_ticker = '001680'
    tester = fetch_stock(ticker=t_ticker)

    print(tester.name)
    print(tester.currency)
    print(tester.ohlcv)
    print(tester.summary)
    print(tester.products)
    print(tester.annual_stat)
    print(tester.quarter_stat)
    print(tester.multifactor)
    print(tester.benchmark_return)
    print(tester.benchmark_multiple)
    print(tester.consensus)
    print(tester.foreign_rate)
    print(tester.short_sell)
    print(tester.short_balance)
    print(tester.expenses)
    print(tester.nps)
    print(tester.multiple_band)
    print(tester.multiple_series)

