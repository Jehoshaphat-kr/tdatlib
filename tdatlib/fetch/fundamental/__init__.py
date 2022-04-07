from tdatlib.fetch.fundamental._fnguide import fnguide
from inspect import currentframe as inner
import pandas as pd


class fundamental_kr(fnguide):

    def __init__(self, ticker:str):
        super().__init__(ticker=ticker)
        return

    def __checkattr__(self, name:str) -> str:
        if not hasattr(self, f'__{name}'):
            _func = self.__getattribute__(f'_get_{name}')
            self.__setattr__(f'__{name}', _func())
        return f'__{name}'

    @property
    def name(self) -> str:
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def summary(self) -> str:
        """
        기업 개요 요약본
        
        1991년 1월에 설립되어 1994년 법인전환 후 2000년 3월에 코스닥시장에 상장한 무선통신장비 전문 제조 기업임.
        동사 및 종속회사는 무선통신 기지국에 장착되는 각종 장비 및 부품류 등을 생산, 판매하는 RF사업과 ...
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def products(self) -> pd.Series:
        """
        제품 구성 비율

        IM        42.05
        반도체    30.77
        CE        14.26
        DP        12.92
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def stat_annual(self) -> pd.DataFrame:
        """
        연간 재무 요약

                       매출액  영업이익  영업이익(발표기준)  ...   PBR  발행주식수  배당수익률
        2017/12     2395754.0  536450.0            536450.0  ...  1.76   6454925.0        1.67
        2018/12     2437714.0  588867.0            588867.0  ...  1.10   5969783.0        3.66
        2019/12     2304009.0  277685.0            277685.0  ...  1.49   5969783.0        2.54
        2020/12     2368070.0  359939.0            359939.0  ...  2.06   5969783.0        3.70
        2021/12     2796048.0  516339.0            516339.0  ...  1.80   5969783.0        1.84
        2022/12(E)  3169958.0  604994.0                 NaN  ...  1.41         NaN         NaN
        2023/12(E)  3383546.0  676872.0                 NaN  ...  1.26         NaN         NaN
        2024/12(E)  3570114.0  673980.0                 NaN  ...  1.13         NaN         NaN
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))


    @property
    def stat_quarter(self) -> pd.DataFrame:
        """
        분기 재무 요약

                       매출액  영업이익  영업이익(발표기준)  당기순이익  ...  PER   PBR  발행주식수  배당수익률
        2020/09      81288.0    13019.0             13019.0     10845.0  ...  NaN  1.15   728002.0          NaN
        2020/12      79662.0     9589.0              9589.0     17704.0  ...  NaN  1.59   728002.0         0.99
        2021/03      84942.0    13244.0             13244.0      9926.0  ...  NaN  1.76   728002.0          NaN
        2021/06     103217.0    26946.0             26946.0     19884.0  ...  NaN  1.62   728002.0          NaN
        2021/09     118053.0    41718.0             41718.0     33153.0  ...  NaN  1.23   728002.0          NaN
        2021/12(E)  123607.0    41844.0                 NaN     33903.0  ...  NaN   NaN        NaN          NaN
        2022/03(E)  112451.0    30024.0                 NaN     21875.0  ...  NaN   NaN        NaN          NaN
        2022/06(E)  115935.0    28307.0                 NaN     17382.0  ...  NaN   NaN        NaN          NaN
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def multifactor(self) -> pd.DataFrame:
        """
        멀티 팩터

                     SK하이닉스 반도체(업종)
        팩터
        베타               0.80         0.31
        배당성            -0.08        -1.03
        수익건전성         1.09        -0.12
        성장성             0.28        -0.05
        기업투자          -0.67        -0.14
        거시경제 민감도   -0.18        -0.32
        모멘텀            -0.34         0.20
        단기 Return        0.35         0.50
        기업규모           0.84        -2.36
        거래도            -0.14         0.68
        밸류               0.16        -0.36
        변동성            -0.24         0.64
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def benchmark_return(self) -> pd.DataFrame:
        """
        벤치마크 지표와 수익률 비교

                                              (Daily) 3M                          (Weekly) 1Y
                    SK하이닉스  코스피 전기,전자   KOSPI  SK하이닉스  코스피 전기,전자  KOSPI
        TRD_DT
        2021-01-15         NaN              NaN      NaN      100.00           100.00  100.00
        2021-01-22         NaN              NaN      NaN       99.69            98.44   99.13
        2021-01-29         NaN              NaN      NaN       97.70            97.66   99.10
        ...                ...              ...      ...         ...              ...     ...
        2022-01-05      137.16           113.68   101.29         NaN              NaN     NaN
        2022-01-06      136.61           112.58   100.14         NaN              NaN     NaN
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def benchmark_multiple(self) -> pd.DataFrame:
        """
        기초 배수 상대 지표

                                               PER                               EV/EBITA                                    ROE
              SK하이닉스  코스피 전기,전자  코스피   SK하이닉스  코스피 전기,전자  코스피   SK하이닉스  코스피 전기,전자  코스피
        2019       34.15            21.90    20.01         6.76              6.85    7.21         4.23              6.11    4.69
        2020       18.14            19.87    22.35         6.37              8.06    8.57         9.53              9.26    5.26
        2021E       9.72            13.28    11.10         4.27              4.65    6.44        16.86             14.15   11.62
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def consensus(self) -> pd.DataFrame:
        """
        컨센서스(투자의견)

                    투자의견  목표주가   종가
        날짜
        2021-03-15      3.96    104875  81800
        2021-03-16      3.96    104875  82800
        2021-03-17      3.96    105304  82300
        ...              ...       ...    ...
        2022-03-08      3.96     99208  69500
        2022-03-10      3.96     99208  71200
        2022-03-11      3.96     99208  70000
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def foreign_rate(self) -> pd.DataFrame:
        """
        외국인 보유율

                               (Daily) 3M             (Weekly) 1Y            (Monthly) 3Y
                      종가 외국인보유비중     종가 외국인보유비중     종가 외국인보유비중
        날짜
        2019-01-01    NaN            NaN      NaN             NaN    42369          56.04
        2019-02-01    NaN            NaN      NaN             NaN    46309          56.72
        2019-03-01    NaN            NaN      NaN             NaN    44560          56.75
        ...           ...            ...      ...             ...      ...            ...
        2022-01-05  77400          51.99      NaN             NaN      NaN            NaN
        2022-01-06  76900          52.03      NaN             NaN      NaN            NaN
        2022-01-07  78300          52.11    77980           52.02      NaN            NaN
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def short_sell(self) -> pd.DataFrame:
        """
        차입 공매도 비중

                   차입공매도비중  수정 종가
        날짜
        2021-01-11              0    133000
        2021-01-18              0    130000
        2021-01-25           0.03    135000
               ...            ...       ...
        2021-12-20           2.58    120500
        2021-12-27           1.18    126000
        2022-01-03           0.98    128500
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def short_balance(self) -> pd.DataFrame:
        """
        대차 잔고 비중
                    대차잔고비중   수정 종가
        날짜
        2021-01-11          1.95      133000
        2021-01-18          2.07      130000
        2021-01-25          2.11      135000
               ...           ...         ...
        2021-12-20          2.71      120500
        2021-12-27          2.68      126000
        2022-01-03          2.36      128500
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def expenses(self) -> pd.DataFrame:
        """
        제반 비용
        
                판관비율  매출원가율  R&D투자비중  무형자산처리비중  당기비용처리비중
        2016/12      NaN         NaN         7.33             0.34               6.99
        2017/12    23.64       53.97         7.01             0.19               6.83
        2018/12    21.53       54.31         7.65             0.12               7.53
        2019/12    24.04       63.91         8.77             0.12               8.65
        2020/12    23.79       61.02         8.96             0.05               8.92
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def multiple_series(self) -> pd.DataFrame:
        """
        시계열 투자배수
        
                       BPS    PER   PBR    EPS   DIV    DPS
        날짜
        2020-04-07  331214  12.95  1.17  29841  2.85  11000
        2020-04-08  331214  12.94  1.17  29841  2.85  11000
        2020-04-09  331214  13.09  1.18  29841  2.82  11000
        2020-04-10  331214  12.92  1.16  29841  2.85  11000
        2020-04-13  331214  12.82  1.15  29841  2.88  11000
        ...            ...    ...   ...    ...   ...    ...
        2022-04-01  369358  18.20  1.60  32418  2.54  15000
        2022-04-04  369358  18.57  1.63  32418  2.49  15000
        2022-04-05  369358  18.66  1.64  32418  2.48  15000
        2022-04-06  369358  19.46  1.71  32418  2.38  15000
        2022-04-07  369358  19.31  1.69  32418  2.40  15000
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def multiple_band(self) -> pd.DataFrame:
        """
        투자배수 밴드

                  수정주가      9.30X     11.78X     14.26X     16.73X     19.21X
        날짜
        2017/12/01  493000  310022.57  392611.91  475201.26   557790.6  640379.95
        2018/01/01  515000  305848.49  387325.87  468803.25  550280.63  631758.01
        2018/02/01  512000  301674.41  382039.82  462405.23  542770.65  623136.06
        2018/03/01  479000  297500.33  376753.77  456007.22  535260.67  614514.12
        2018/04/01  433500  293326.25  371467.73  449609.21  527750.69  605892.17
        ...            ...        ...        ...        ...        ...        ...
        2024/08/01       -  400141.49  506738.32  613335.15  719931.99  826528.82
        2024/09/01       -  396636.12  502299.13  607962.14  713625.15  819288.15
        2024/10/01       -  393130.75  497859.93  602589.12   707318.3  812047.49
        2024/11/01       -  389625.38  493420.74   597216.1  701011.46  804806.82
        2024/12/01       -     386120  488981.54  591843.08  694704.62  797566.16
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))


if __name__ == "__main__":
    # pd.set_option('display.expand_frame_repr', False)

    _ticker = '005930'

    app = fundamental_kr(ticker=_ticker)
    print(app.name)

    # print(app.summary)
    # print(app.products)
    # print(app.astat)
    # print(app.qstat)
    # print(app.multifactor)
    # print(app.benchmark_return)
    # print(app.benchmark_multiple)
    # print(app.consensus)
    # print(app.foreign_rate)
    # print(app.short_sell)
    # print(app.short_balance)
    # print(app.expenses)
    # print(app.multiple_series)
    # print(app.multiple_band)