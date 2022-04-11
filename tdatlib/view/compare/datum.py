from tdatlib import market_kr, ohlcv, fundamental_kr
import pandas as pd
import numpy as np


class datum:

    def __init__(self, tickers:list or np.array, period:int=5):
        self.tickers, self.period = tickers, period
        for ticker in tickers:
            setattr(self, f'__{ticker}t', ohlcv(ticker=ticker, period=period))
            setattr(self, f'__{ticker}f', fundamental_kr(ticker=ticker))
        return

    @property
    def names(self) -> list:
        """ 종목명 리스트 """
        return [self.__getattribute__(f'__{ticker}t').name for ticker in self.tickers]
    
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
        objs = dict()
        for ticker in self.tickers:
            attr = self.__getattribute__(f'__{ticker}t')
            objs[attr.name] = attr.ohlcv.종가
        return pd.concat(objs=objs, axis=1)

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
        for ticker in self.tickers:
            attr = self.__getattribute__(f'__{ticker}t')
            rel = attr.relative_return.copy()
            for col in rel.columns:
                objs[(col, attr.name)] = rel[col]
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
        objs = dict()
        for ticker in self.tickers:
            attr = self.__getattribute__(f'__{ticker}t')
            objs[attr.name] = attr.ta.volume_mfi
        return pd.concat(objs=objs, axis=1)

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
        objs = dict()
        for ticker in self.tickers:
            attr = self.__getattribute__(f'__{ticker}t')
            objs[attr.name] = attr.ta.momentum_rsi
        return pd.concat(objs=objs, axis=1)

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
        objs = dict()
        for ticker in self.tickers:
            attr = self.__getattribute__(f'__{ticker}t')
            objs[attr.name] = attr.ta.trend_cci
        return pd.concat(objs=objs, axis=1)

    @property
    def rel_sharpe_ratio(self) -> pd.DataFrame:
        """
        샤프 비율 데이터
        :return:
        """
        objs = dict()
        for ticker in self.tickers:
            cap = np.log(self.icm.loc[ticker, '시가총액'])
            attr = self.__getattribute__(f'__{ticker}t')
            data = [
                {f'cagr': attr.cagr(days=days), f'risk': attr.volatility(days=days), 'term':term, 'cap':cap}
                for term, days in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]
            ]
            objs[attr.name] = pd.DataFrame(data=data).set_index(keys='term')
        return pd.concat(objs, axis=1)


if __name__ == "__main__":
    # t_tickers = ['TSLA', 'MSFT', 'GOOG', 'ZM']
    t_tickers = ['005930', '000660', '058470', '000990']

    t_series = datum(tickers=t_tickers, period=1)
    # print(t_series.price)
    # print(t_series.icm)
    # print(t_series.rel_yield)
    # print(t_series.rel_yield['1Y'].dropna())
    # print(t_series.rel_mfi)
    # print(t_series.rel_rsi)
    # print(t_series.rel_cci)
    print(t_series.sharpe_ratio)
