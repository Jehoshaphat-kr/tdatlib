import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta


def normalize(time_series: pd.Series or np.array, a: float = 0, b: float = 1) -> pd.Series:
    """
    정규화
    :param time_series: 시계열 데이터
    :param a: 정규 최소 값
    :param b: 정규 최대 값
    """
    return (b - a) * (time_series - time_series.min()) / (time_series.max() - time_series.min()) + a


def typify(ohlcv: pd.DataFrame) -> pd.Series:
    """
    가격 전형화
    :param ohlcv: 가격
    """
    if not ('종가' in ohlcv.columns and '고가' in ohlcv.columns and '저가' in ohlcv.columns):
        raise KeyError
    return (1 / 3) * ohlcv.종가 + (1 / 3) * ohlcv.고가 + (1 / 3) * ohlcv.저가


class corr(object):
    """
    시계열 상관성 평가 모델
    """
    _w = [
        [1], [1],
        [0.670, 0.330],
        [0.450, 0.330, 0.220],
        [0.334, 0.277, 0.222, 0.167],
        [0.267, 0.233, 0.200, 0.167, 0.113],
        [0.224, 0.200, 0.177, 0.155, 0.133, 0.111],
        [0.193, 0.174, 0.158, 0.142, 0.127, 0.111, 0.095],
        [0.168, 0.155, 0.143, 0.131, 0.118, 0.107, 0.095, 0.083]
    ]

    def __init__(self, l: pd.Series, r: pd.Series, l_name: str = 'Left', r_name: str = 'Right'):
        # Align
        j = pd.concat(objs={'L': l, 'R': r}, axis=1).dropna()
        self._j = j[j.index.isin(l.index)]
        self.l, self.r = self._j.L, self._j.R
        self._lname, self._rname = l_name, r_name
        return

    @property
    def coeff(self) -> float:
        """
        전체 시계열 상관계수
        """
        return self._j.corr().iloc[0, 1]

    @property
    def by_period(self) -> pd.DataFrame:
        """
        기간 별 상관계수

               3개월     6개월       1년       2년       3년       5년    10년      전체
        0  -0.773963 -0.715229 -0.813411 -0.053977 -0.049446 -0.299048  0.0658 -0.128364
        """
        if not hasattr(self, '__by_period'):
            days = (self._j.index[-1] - self._j.index[0]).days
            gaps = [0, 92, 183, 365, 365 * 2, 365 * 3, 365 * 5, 365 * 10]
            nums = [i + 1 for i in range(len(gaps) - 1) if gaps[0] < days <= gaps[i + 1]]
            loop = gaps[1:nums[0]] if nums else gaps[1:]

            cols = ['3개월', '6개월', '1년', '2년', '3년', '5년', '10년', '전체']
            data = [
                self._j[self._j.index >= (self._j.index[-1] - timedelta(g))].corr().iloc[0, 1] for g in loop
            ] + [self.coeff]
            self.__setattr__('__by_period', pd.DataFrame(data=[data], columns=cols[:len(data)], index=[0]))
        return self.__getattribute__('__by_period')

    @property
    def coeffw(self) -> float:
        """
        가중치 테이블
        N       1      2      3      4      5      6      7      8      기간
        1   1.000  0.670  0.450  0.334  0.267  0.224  0.193  0.168  |  3개월
        2          0.330  0.330  0.277  0.233  0.200  0.174  0.155  |  6개월
        3                 0.220  0.222  0.200  0.177  0.158  0.143  |  1년
        4                        0.167  0.167  0.155  0.142  0.131  |  2년
        5                               0.133  0.133  0.127  0.118  |  3년
        6                                      0.111  0.111  0.107  |  5년
        7                                             0.095  0.095  |  10년
        8                                                    0.083  |  Max.
        """
        return (self.by_period.iloc[0].to_numpy() * np.array(self._w[len(self.by_period.columns)])).sum()

    @property
    def by_rolling(self) -> pd.DataFrame:
        """
        전후 6개월 내 지표간 선/후행성 조사

             shifter     cursor  days     coeff  coeffabs
        30       -63 2022-07-27   -96  0.001387  0.001387
        31       -61 2022-07-29   -94 -0.010474  0.010474
        29       -65 2022-07-25   -98  0.012779  0.012779
        ..       ...        ...   ...       ...       ...
        111       99 2023-03-27   147 -0.390103  0.390103
        114      105 2023-04-04   155 -0.390240  0.390240
        113      103 2023-04-02   153 -0.390462  0.390462
        """
        if not hasattr(self, '__by_rolling'):
            prev_day = self.l.index[-1] - timedelta(days=int(6 * 30.5))
            samples = len(self.r.index[self.r.index >= prev_day])
            nums = np.arange(start=-samples, stop=samples + 1, step=2)

            prev, curr = self.r.index[0], self.r.index[-1]
            data = list()
            for i in nums:
                rs = self.r.shift(i).copy()
                coeff = pd.concat(objs=[self.l, rs], axis=1).dropna().corr().iloc[0, 1]
                if i <= 0: # 선행성 상관계수
                    cursor = rs.dropna().index[-1]
                    days = self.l.index[-1] - cursor
                    data.append([i, cursor, days, coeff, -1, abs(coeff)])
                else: # 후행성 상관계수
                    dt = (rs.dropna().index[0] - prev)
                    curr += dt
                    prev = rs.dropna().index[0]
                    data.append([i, curr, curr - self.l.index[-1], coeff, 1, abs(coeff)])
            df = pd.DataFrame(data=data, columns=['shifter', 'cursor', 'days', 'coeff', 'sign', 'coeffabs'])
            df.days = df.days.dt.days * df.sign
            df = df.drop(columns=['sign'])
            self.__setattr__('__by_rolling', df.sort_values(by=['coeffabs']))
        return self.__getattribute__('__by_rolling')

    @property
    def coeffr(self) -> float:
        df = self.by_rolling.copy()
        return df.iloc[-1, -2]

    @property
    def trace_l(self) -> go.Scatter:
        return go.Scatter(
            x=self.l.index, y=self.l, name=self._lname,
            visible=True, showlegend=True,
            xhoverformat='%Y/%m/%d', hovertemplate='%{x}<br>%{y}'
        )

    @property
    def trace_r(self) -> go.Scatter:
        return go.Scatter(
            x=self.r.index, y=self.r, name=self._rname,
            visible=True, showlegend=True,
            xhoverformat='%Y/%m/%d', hovertemplate='%{x}<br>%{y}'
        )

    @property
    def trace_rshift(self) -> [go.Scatter]:
        df = self.by_rolling.tail(5)
        return [go.Scatter(
            x=self.r.shift(i[1]).index, y=self.r.shift(i[1]), name=f'{self._rname}<br>({i[3]}) shifted',
            visible='legendonly', showlegend=True, mode='lines', line=dict(dash='dot'),
            xhoverformat='%Y/%m/%d', hovertemplate='%{x}<br>%{y}'
        ) for i in df.itertuples()]

    @property
    def trace_corr(self) -> go.Scatter:
        return go.Scatter(
            x=normalize(self.l, -1, 1), y=normalize(self.r, -1, 1), name='산포도',
            meta=self._j.index, text=self.l, customdata=self.r, mode='markers',
            hovertemplate='%{meta}<br>x = %{x}(%{text})<br>y = %{y}(%{customdata})<extra></extra>'
        )



if __name__ == "__main__":
    from tdatlib import stock, macro, market

    period = 5

    macro = macro.ecos
    index = market.index
    stock = stock.kr(ticker='105560')
    # stock = stock.kr(ticker='005930')
    macro.period = index.period = stock.period = period

    # exchange = price_generalize(macro.원달러환율)
    # price = price_generalize(stock.ohlcv)
    kospi = index.kospi.종가
    exchange = macro.원달러환율.종가
    price = stock.ohlcv.종가

    relation = corr(price, exchange)
    # print(relation.by_period)
    print(relation.by_rolling)
    # print(relation.coeffr)