from tdatlib.fetch.market import market
from tdatlib.interface.stock import interface_stock
import pandas as pd
import numpy as np


class interface_compare(object):

    def __init__(self, tickers:list or np.array, period:int=5):
        self.tickers, self.period = tickers, period
        for ticker in tickers:
            setattr(self, f'__{ticker}', interface_stock(ticker=ticker, period=period))
        self.names = [self.__getattribute__(f'__{ticker}').name for ticker in self.tickers]
        self.market = market()
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
            objs={n: self.__getattribute__(f'__{t}').ohlcv.종가 for n, t in zip(self.names, self.tickers)},
            axis=1
        )

    @property
    def rel_icm(self) -> pd.DataFrame:
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
            icm = self.market.icm
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
            rel = self.__getattribute__(f'__{ticker}').rr.copy()
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
            rel = self.__getattribute__(f'__{ticker}').dd.copy()
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
            objs={n:self.__getattribute__(f'__{t}').ta.volume_mfi for n, t in zip(self.names, self.tickers)},
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
            objs={n: self.__getattribute__(f'__{t}').ta.momentum_rsi for n, t in zip(self.names, self.tickers)},
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
            objs={n: self.__getattribute__(f'__{t}').ta.momentum_stoch for n, t in zip(self.names, self.tickers)},
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
            objs={n: self.__getattribute__(f'__{t}').ta.trend_cci for n, t in zip(self.names, self.tickers)},
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
            objs={n: self.__getattribute__(f'__{t}').ta.trend_vortex_ind_diff for n, t in zip(self.names, self.tickers)},
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
            objs={n: self.__getattribute__(f'__{t}').ta.volatility_bbp for n, t in zip(self.names, self.tickers)},
            axis=1
        )

    @property
    def rel_sharpe_ratio(self) -> pd.DataFrame:
        """
        샤프 비율 데이터
        :return:
                                     삼성전자  ...                         DB하이텍
                   cagr       risk        cap  ...       cagr       risk        cap
        3M   -42.314782  17.496205  33.637239  ... -39.919069  38.646100  28.744766
        6M    -3.154487  19.205607  33.637239  ...  84.220739  41.831750  28.744766
        1Y   -18.389423  18.531063  33.637239  ...  24.727273  40.790418  28.744766
        2Y    18.566315  23.887624  33.637239  ...  75.786521  46.544911  28.744766
        3Y    13.167067  25.856999  33.637239  ...  72.348076  49.691325  28.744766
        5Y    10.136469  25.942737  33.637239  ...  26.353973  48.032697  28.744766
        """
        objs = dict()
        for name, ticker in zip(self.names, self.tickers):
            attr = self.__getattribute__(f'__{ticker}')
            objs[(name, 'cagr')] = attr.cagr.loc[ticker].tolist()
            objs[(name, 'risk')] = attr.volatility.loc[ticker].tolist()
            objs[(name, 'cap')] = [np.log(self.rel_icm.loc[ticker, '시가총액'])] * 6
        return pd.DataFrame(data=objs, index=['3M', '6M', '1Y', '2Y', '3Y', '5Y'])

    @property
    def rel_profit(self) -> pd.DataFrame:
        """
        분기별 영업이익률, 배당수익률, ROA 및 ROE
        :return: (주석 생략)
        """
        objs = dict()
        for name, ticker in zip(self.names, self.tickers):
            data = self.__getattribute__(f'__{ticker}').annual_stat[['영업이익률', '배당수익률', 'ROA', 'ROE']]
            for col in data.columns:
                objs[(col, name)] = data[col]
        return pd.concat(objs=objs, axis=1)[:-2]

    @property
    def rel_multiple(self) -> pd.DataFrame:
        """
        투자 배수: PSR, EV/EBITDA, PER, PBR
        :return:
                       매출액  EBITDAPS    종가  ...        SPS   PSR  EV/EBITDA
        종목명                                   ...
        삼성전자    2796048.0  12643.22   67000  ...   46836.68  1.43       5.30
        SK하이닉스   429978.0  31687.86  111000  ...   59062.72  1.88       3.50
        DB하이텍      12147.0  12219.13   69300  ...   27358.98  2.53       5.67
        리노공업       2802.0   8492.08  175800  ...   18382.97  9.56      20.70
        동진쎄미켐    11613.0   3515.13   36500  ...   22587.02  1.62      10.38
        솔브레인      10239.0  30523.15  233900  ...  131630.95  1.78       7.66
        """
        objs = list()
        for name, ticker in zip(self.names, self.tickers):
            nps = self.__getattribute__(f'__{ticker}').nps
            stat = self.__getattribute__(f'__{ticker}').annual_stat
            key = [_ for _ in ['매출액', '순영업수익', '이자수익', '보험료수익'] if _ in stat.columns][0]
            idx = [i for i in stat.index if not '(' in i][-1]
            objs.append(dict(종목명=name, 종목코드=ticker, 매출액=stat.loc[idx, key], EBITDAPS=nps.iloc[-1]['EBITDAPS']))
        sales = pd.DataFrame(data=objs).set_index(keys='종목코드')
        multiple = sales.join(self.rel_icm[['종가', 'PER', 'EPS', 'PBR', 'BPS', '상장주식수']])
        multiple['SPS'] = round(multiple['매출액'] * 100000000 / multiple['상장주식수'], 2)
        multiple['PSR'] = round(multiple['종가'] / multiple['SPS'], 2)
        multiple['EV/EBITDA'] = round(multiple['종가'] / multiple['EBITDAPS'], 2)
        return multiple.set_index(keys='종목명')

    @property
    def rel_growth(self) -> pd.DataFrame:
        """
        성장 지표
        :return:
                 매출증가율  영업이익증가율  EPS증가율   PEG
        종목명
        삼성전자     18.07            43.45      50.40  0.35
        SK하이닉스   34.79           147.58     101.93  0.16
        DB하이텍     29.79            66.78      90.86  0.21
        리노공업     39.20            50.32      87.45  0.56
        동진쎄미켐   23.83             4.35      21.11  1.08
        솔브레인    117.80            81.54     134.76  0.22
        """
        icm = self.rel_icm
        growth = pd.DataFrame()
        for name, ticker in zip(self.names, self.tickers):
            stat = self.__getattribute__(f'__{ticker}').annual_stat
            key = [_ for _ in ['매출액', '순영업수익', '이자수익', '보험료수익'] if _ in stat.columns][0]
            data = round(100 * stat[[key, '영업이익', 'EPS(원)']].pct_change(), 2)
            data = data[1:].join(stat['PER'], how='left')
            data['PEG'] = round(data['PER'] / data['EPS(원)'], 2)
            data = data.drop(columns=['PER']).rename(columns={
                key:'매출증가율', '영업이익':'영업이익률', 'EPS(원)':'EPS증가율'
            })

            objs = dict()
            for i in data.index[:-2]:
                _data = data.loc[i].to_dict()
                objs[i] = pd.DataFrame(data=_data, index=[name])
                if i.startswith(str(self.market.kr_date.year - 1)):
                    _data['PEG'] = round(icm.loc[ticker, 'PER'] / _data['EPS증가율'], 2)
                    objs[f'{self.market.kr_date.year}/현재'] = pd.DataFrame(data=_data, index=[name])
            growth = pd.concat(objs=[growth, pd.concat(objs=objs, axis=1)], axis=0)
        return growth


if __name__ == "__main__":
    # t_tickers = ['TSLA', 'MSFT', 'GOOG', 'ZM']
    # t_tickers = ['005930', '000660', '058470', '000990']
    # t_tickers = ['005930', '000660', '000990', '058470', '005290', '357780']
    t_tickers = ['105560', '055550', '316140', '024110']

    t_series = interface_compare(tickers=t_tickers, period=5)
    print(t_series.price)
    print(t_series.rel_icm)
    print(t_series.rel_icm.columns)
    print(t_series.rel_yield)
    print(t_series.rel_yield['1Y'].dropna())
    print(t_series.rel_drawdown)
    print(t_series.rel_mfi)
    print(t_series.rel_rsi)
    print(t_series.rel_stoch)
    print(t_series.rel_cci)
    print(t_series.rel_vortex)
    print(t_series.rel_bb)
    print(t_series.rel_sharpe_ratio)

    print(t_series.rel_profit)
    print(t_series.rel_multiple)
    print(t_series.rel_growth)