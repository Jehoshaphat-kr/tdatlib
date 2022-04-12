from tdatlib import market_kr, ohlcv, narrative_kr
import pandas as pd
import numpy as np


class datum:

    def __init__(self, tickers:list or np.array, period:int=5):
        self.tickers, self.period = tickers, period
        for ticker in tickers:
            setattr(self, f'__{ticker}t', ohlcv(ticker=ticker, period=period))
            setattr(self, f'__{ticker}f', narrative_kr(ticker=ticker))
        self.names = [self.__getattribute__(f'__{ticker}t').name for ticker in self.tickers]
        return

    @property
    def price(self) -> pd.DataFrame:
        """
        가격[종가] 데이터
        :return:
                 삼성전자  SK하이닉스  리노공업  DB하이텍
        날짜
        2021-04-12  83200      137500    158200     55000
        2021-04-13  84000      139500    160100     55200
        2021-04-14  84000      137000    159900     54700
        ...           ...         ...       ...       ...
        2022-04-07  68000      113500    174600     70000
        2022-04-08  67800      112000    175500     69700
        2022-04-11  67800      112000    175100     69700
        """
        return pd.concat(
            objs={n: self.__getattribute__(f'__{t}t').ohlcv.종가 for n, t in zip(self.names, self.tickers)},
            axis=1
        )

    @property
    def icm(self) -> pd.DataFrame:
        """
        IPO, 시가 총액(Market Cap) 및 기초 배수(Multiples)
        :return:
                    종목명         IPO    종가         시가총액  ...   PBR     EPS   DIV     DPS
        종목코드                                                 ...
        005930    삼성전자  1975-06-11   67800  405945213400000  ...  1.72  3841.0  4.42  2994.0
        000660  SK하이닉스  1996-12-26  112000   81900266062500  ...  1.57  6952.0  1.04  1170.0
        000990    DB하이텍  1975-12-12   69700    3103461301200  ...  3.90  3822.0  0.50   350.0
        058470    리노공업  2001-12-18  175500    2670463224000  ...  7.93  3648.0  0.85  1500.0
        """
        if not hasattr(self, '__icm'):
            icm = market_kr().icm
            self.__setattr__('__icm', icm[icm.index.isin(self.tickers)].copy())
        return self.__getattribute__('__icm')

    @property
    def rel_yield(self) -> pd.DataFrame:
        """
        상대 수익률 비교 데이터
        :return:
                           3M        6M         1Y  ...           2Y           3Y           5Y
                     삼성전자  삼성전자   삼성전자  ... 케이엠더블유 케이엠더블유 케이엠더블유
        날짜                                        ...
        2017-04-10        NaN       NaN        NaN  ...          NaN         NaN     0.000000
        2017-04-11        NaN       NaN        NaN  ...          NaN         NaN     3.553114
        2017-04-12        NaN       NaN        NaN  ...          NaN         NaN     5.769231
        ...               ...       ...        ...  ...          ...         ...          ...
        2022-04-06 -10.923277 -4.329609 -19.126328  ...   -44.859038  113.141026   508.974359
        2022-04-07 -11.573472 -5.027933 -19.716647  ...   -45.439469  110.897436   502.564103
        2022-04-08 -11.833550 -5.307263 -19.952774  ...   -45.771144  109.615385   498.901099
        """
        objs = dict()
        for name, ticker in zip(self.names, self.tickers):
            rel = self.__getattribute__(f'__{ticker}t').relative_return.copy()
            for col in rel.columns:
                objs[(col, name)] = rel[col]
        return pd.concat(objs=objs, axis=1)

    @property
    def rel_drawdown(self) -> pd.DataFrame:
        """
        상대 낙폭 비교 데이터
        :return:
                           3M         6M         1Y  ...         2Y         3Y         5Y
                     삼성전자   삼성전자   삼성전자  ...   DB하이텍   DB하이텍   DB하이텍
        날짜                                         ...
        2021-04-12        NaN        NaN   0.000000  ...   0.000000   0.000000   0.000000
        2021-04-13        NaN        NaN   0.000000  ...   0.000000   0.000000   0.000000
        2021-04-14        NaN        NaN   0.000000  ...  -0.905797  -0.905797  -0.905797
        ...               ...        ...        ...  ...        ...        ...        ...
        2022-04-07 -13.814956 -15.527950 -19.143876  ... -17.550059 -17.550059 -17.550059
        2022-04-08 -14.068441 -15.776398 -19.381688  ... -17.903416 -17.903416 -17.903416
        2022-04-11 -13.941698 -15.652174 -19.262782  ... -19.199058 -19.199058 -19.199058
        """
        objs = dict()
        for name, ticker in zip(self.names, self.tickers):
            rel = self.__getattribute__(f'__{ticker}t').drawdown.copy()
            for col in rel.columns:
                objs[(col, name)] = rel[col]
        return pd.concat(objs=objs, axis=1)

    @property
    def rel_mfi(self) -> pd.DataFrame:
        """
        상대 자금 유입 지수 (MFI: Money Flow Index)
        :return:
                     삼성전자  SK하이닉스   리노공업    DB하이텍
        날짜
        2017-04-10        NaN         NaN        NaN        NaN
        2017-04-11        NaN         NaN        NaN        NaN
        2017-04-12        NaN         NaN        NaN        NaN
        ...               ...         ...        ...        ...
        2022-04-06  17.281504   38.943384  36.886421  58.799685
        2022-04-07  16.810691   29.891098  35.076959  52.413128
        2022-04-08  16.514520   29.648873  35.755695  42.692124
        """
        return pd.concat(
            objs={n:self.__getattribute__(f'__{t}t').ta.volume_mfi for n, t in zip(self.names, self.tickers)},
            axis=1
        )

    @property
    def rel_rsi(self) -> pd.DataFrame:
        """
        상대 RSI 비교 데이터
        :return:
                     삼성전자   SK하이닉스     리노공업  케이엠더블유
        날짜
        2017-04-10        NaN          NaN          NaN          NaN
        2017-04-11        NaN          NaN          NaN          NaN
        2017-04-12        NaN          NaN          NaN          NaN
        ...               ...          ...          ...          ...
        2022-04-06  35.260481    37.343072    38.082934    52.349595
        2022-04-07  32.860383    38.468218    37.962012    50.258491
        2022-04-08  31.924316    36.358833    39.814255    49.052700
        """
        return pd.concat(
            objs={n: self.__getattribute__(f'__{t}t').ta.momentum_rsi for n, t in zip(self.names, self.tickers)},
            axis=1
        )

    @property
    def rel_stoch(self) -> pd.DataFrame:
        """
        상대 RSI Stochastic 비교 데이터
        :return:
                    삼성전자  SK하이닉스   리노공업   DB하이텍
        날짜
        2017-04-12        NaN        NaN        NaN        NaN
        2017-04-13        NaN        NaN        NaN        NaN
        2017-04-14        NaN        NaN        NaN        NaN
        ...               ...        ...        ...        ...
        2022-04-07   0.000000  21.428571  23.834197   5.555556
        2022-04-08   2.857143  10.714286  29.729730  12.000000
        2022-04-11  13.157895   7.142857  21.081081   1.000000
        """
        return pd.concat(
            objs={n: self.__getattribute__(f'__{t}t').ta.momentum_stoch for n, t in zip(self.names, self.tickers)},
            axis=1
        )

    @property
    def rel_cci(self) -> pd.DataFrame:
        """
        상대 CCI 데이터
        :return:
                      삼성전자  SK하이닉스    리노공업    DB하이텍
        날짜
        2021-04-12         NaN         NaN         NaN        NaN
        2021-04-13         NaN         NaN         NaN        NaN
        2021-04-14         NaN         NaN         NaN        NaN
        ...                ...         ...         ...        ...
        2022-04-07 -211.335862 -130.311615 -200.256566 -77.915152
        2022-04-08 -191.160809 -129.144852 -129.746884 -93.428571
        2022-04-11 -166.514042 -124.137931 -132.607754 -97.206166
        """
        return pd.concat(
            objs={n: self.__getattribute__(f'__{t}t').ta.trend_cci for n, t in zip(self.names, self.tickers)},
            axis=1
        )

    @property
    def rel_vortex(self) -> pd.DataFrame:
        """
        상대 VORTEX 비교 데이터
        :return:
                    삼성전자  SK하이닉스  리노공업   DB하이텍
        날짜
        2017-04-12       NaN         NaN       NaN       NaN
        2017-04-13       NaN         NaN       NaN       NaN
        2017-04-14       NaN         NaN       NaN       NaN
        ...              ...         ...       ...       ...
        2022-04-07 -0.391753   -0.426966 -0.574737  0.013072
        2022-04-08 -0.445652   -0.426966 -0.500000 -0.178451
        2022-04-11 -0.440860   -0.443182 -0.518828 -0.119048
        """
        return pd.concat(
            objs={n: self.__getattribute__(f'__{t}t').ta.trend_vortex_ind_diff for n, t in zip(self.names, self.tickers)},
            axis=1
        )

    @property
    def rel_bb(self) -> pd.DataFrame:
        """
        상대 볼린저밴드 신호 비교 데이터
        :return:
                    삼성전자  SK하이닉스  리노공업   DB하이텍
        날짜
        2017-04-12       NaN         NaN       NaN       NaN
        2017-04-13       NaN         NaN       NaN       NaN
        2017-04-14       NaN         NaN       NaN       NaN
        ...              ...         ...       ...       ...
        2022-04-07 -0.120035    0.146258  0.009188  0.255423
        2022-04-08 -0.059921    0.088902  0.111689  0.230855
        2022-04-11  0.044824    0.097454  0.077344  0.129972
        """
        return pd.concat(
            objs={n: self.__getattribute__(f'__{t}t').ta.volatility_bbp for n, t in zip(self.names, self.tickers)},
            axis=1
        )

    @property
    def rel_sharpe_ratio(self) -> pd.DataFrame:
        """
        샤프 비율 데이터
        :return:
                                     삼성전자  ...                         DB하이텍
                   cagr       risk        cap  ...       cagr       risk        cap
        term                                   ...
        3M   -42.314782  17.496205  33.637239  ... -39.919069  38.646100  28.744766
        6M    -3.154487  19.205607  33.637239  ...  84.220739  41.831750  28.744766
        1Y   -18.389423  18.531063  33.637239  ...  24.727273  40.790418  28.744766
        2Y    18.566315  23.887624  33.637239  ...  75.786521  46.544911  28.744766
        3Y    13.167067  25.856999  33.637239  ...  72.348076  49.691325  28.744766
        5Y    10.136469  25.942737  33.637239  ...  26.353973  48.032697  28.744766
        """
        objs = dict()
        for name, ticker in zip(self.names, self.tickers):
            cap = np.log(self.icm.loc[ticker, '시가총액'])
            attr = self.__getattribute__(f'__{ticker}t')
            data = [
                {f'cagr': attr.cagr(days=days), f'risk': attr.volatility(days=days), 'term':term, 'cap':cap}
                for term, days in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]
            ]
            objs[name] = pd.DataFrame(data=data).set_index(keys='term')
        return pd.concat(objs, axis=1)

    @property
    def rel_profit(self) -> pd.DataFrame:
        """
        (발표 기준) 영업이익률, ROA, ROE 및 배당수익률 비교 데이터
        :return:
                영업이익률    ROA    ROE  배당수익률
        삼성전자     18.47   9.92  13.92        1.84
        SK하이닉스   28.86  11.48  16.84        1.18
        DB하이텍     32.86  23.23  33.35        0.62
        리노공업     41.80  25.08  27.50        1.26
        동진쎄미켐   11.35   9.58  20.92        0.22
        솔브레인     18.44  19.67  26.28        0.70
        """
        objs = dict()
        for name, ticker in zip(self.names, self.tickers):
            data = self.__getattribute__(f'__{ticker}f').stat_annual
            loc = [i for i in data.index if not '(' in i][-1]
            objs[name] = data.loc[loc, ['영업이익률', '배당수익률', 'ROA', 'ROE']]
        return pd.concat(objs=objs, axis=1).T

    @property
    def rel_profit_estimate(self) -> pd.DataFrame:
        """
        (전망치 기준) 영업이익률, ROA, ROE 및 배당수익률 비교 데이터
        :return:
                영업이익률    ROA    ROE  배당수익률
        삼성전자     18.47   9.92  13.92        1.84
        SK하이닉스   28.86  11.48  16.84        1.18
        DB하이텍     32.86  23.23  33.35        0.62
        리노공업     41.80  25.08  27.50        1.26
        동진쎄미켐   11.35   9.58  20.92        0.22
        솔브레인     18.44  19.67  26.28        0.70
        """
        objs = dict()
        for name, ticker in zip(self.names, self.tickers):
            data = self.__getattribute__(f'__{ticker}f').stat_annual
            loc = [i for i in data.index if '(' in i][0]
            objs[name] = data.loc[loc, ['영업이익률', '배당수익률', 'ROA', 'ROE']]
        return pd.concat(objs=objs, axis=1).T

    @property
    def rel_stat(self) -> pd.DataFrame:
        """
        분기별 영업이익률, 배당수익률, ROA 및 ROE
        :return:
        """
        objs = dict()
        for name, ticker in zip(self.names, self.tickers):
            data = self.__getattribute__(f'__{ticker}f').stat_annual[['영업이익률', '배당수익률', 'ROA', 'ROE']]
            for col in data.columns:
                objs[(col, name)] = data[col]
        return pd.concat(objs=objs, axis=1)


if __name__ == "__main__":
    # t_tickers = ['TSLA', 'MSFT', 'GOOG', 'ZM']
    # t_tickers = ['005930', '000660', '058470', '000990']
    t_tickers = ['005930', '000660', '000990', '058470', '005290', '357780']

    t_series = datum(tickers=t_tickers, period=5)
    # print(t_series.price)
    # print(t_series.icm)
    # print(t_series.icm.columns)
    # print(t_series.rel_yield)
    # print(t_series.rel_yield['1Y'].dropna())
    # print(t_series.rel_drawdown)
    # print(t_series.rel_mfi)
    # print(t_series.rel_rsi)
    # print(t_series.rel_stoch)
    # print(t_series.rel_cci)
    # print(t_series.rel_vortex)
    # print(t_series.rel_bb)
    # print(t_series.rel_sharpe_ratio)

    # print(t_series.rel_profit)
    # print(t_series.rel_profit_estimate)
    print(t_series.rel_stat)
