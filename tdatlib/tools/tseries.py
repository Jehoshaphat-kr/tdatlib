import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta


def align(l:pd.Series or pd.DataFrame, r:pd.Series or pd.DataFrame):
    """
    두 개의 시계열 데이터 정렬(왼쪽 시계열 기준)
    :param l: Left
    :param r: Right
    """
    join = pd.concat(objs={'L':l, 'R':r}, axis=1).dropna()
    join = join[join.index.isin(l.index)]
    return join.L, join.R


def normalize(time_series:pd.Series or np.array, a:float=0, b:float=1) -> pd.Series:
    """
    정규화
    :param time_series: 시계열 데이터 
    :param a: 정규 최소 값
    :param b: 정규 최대 값
    """
    return (b - a) * (time_series - time_series.min()) / (time_series.max() - time_series.min()) + a


def typify(ohlcv:pd.DataFrame) -> pd.Series:
    """
    가격 전형화
    :param ohlcv: 가격
    """
    if not ('종가' in ohlcv.columns and '고가' in ohlcv.columns and '저가' in ohlcv.columns):
        raise KeyError
    return (1/3) * ohlcv.종가 + (1/3) * ohlcv.고가 + (1/3) * ohlcv.저가


def corrcoeff(l:pd.Series, r:pd.Series) -> float:
    """
    상관계수
    :param l: Left
    :param r: Right
    """
    return pd.concat(objs=align(l, r), axis=1).corr(method='pearson', min_periods=1).iloc[0, 1]


def corr_rolling(l:pd.Series, r:pd.Series, month:int) -> pd.DataFrame:
    """
    이동 상관계수 데이터프레임
    :param l: Left
    :param r: Right
    :param month: 이동 범위(개월)
    """
    prev_day = l.index[-1] - timedelta(days=int(month * 30.5))
    samples = len(r.index[r.index >= prev_day])
    index = np.arange(start=-samples, stop=samples + 1, step=5)

    dates = [r.index[-1] + timedelta(int(i)) for i in index]
    data = [[corrcoeff(l, r.shift(i)), i] for i in index]
    return pd.DataFrame(data=data, index=dates, columns=['corrcoef', 'days'])


class corr(object):
    """
    시계열 상관성 평가 모델
    """
    """
    N       1      2      3      4      5      6      7      8
    1   1.000  0.670  0.450  0.334  0.267  0.224  0.193  0.168
    2          0.330  0.330  0.277  0.233  0.200  0.174  0.155
    3                 0.220  0.222  0.200  0.177  0.158  0.143
    4                        0.167  0.167  0.155  0.142  0.131
    5                               0.133  0.133  0.127  0.118
    6                                      0.111  0.111  0.107
    7                                             0.095  0.095
    8                                                    0.083
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

    def __init__(self, l:pd.Series, r:pd.Series, l_name:str='Left', r_name:str='Right'):
        # Align
        j = pd.concat(objs={'L': l, 'R': r}, axis=1).dropna()
        self._j = j[j.index.isin(l.index)]
        self.l, self.r = self._j.L, self._j.R
        self._lname, self._rname = l_name, r_name
        return

    @property
    def by_period(self) -> pd.DataFrame:
        """
        기간 별 상관계수
        """
        length = (self._j.index[-1] - self._j.index[0]).days
        gaps = [0, 92, 183, 365, 365 * 2, 365 * 3, 365 * 5, 365 * 10]
        n = [i + 1 for i in range(len(gaps) - 1) if gaps[0] < length <= gaps[i + 1]]
        loop = gaps[1:n[0]] if n else gaps[1:]

        label = ['3개월', '6개월', '1년', '2년', '3년', '5년', '10년']
        data = [self._j[self._j.index >= (self._j.index[-1] - timedelta(g))].corr().iloc[0, 1] for g in loop]
        data.append(self._j.corr().iloc[0, 1])
        return pd.DataFrame(data=[data], columns=label[:len(data)] + ['전체'], index=[0])

    def _coeffr(self) -> (float, int, int):
        if not hasattr(self, '__coeffr'):
            rolling = corr_rolling(l=self.l, r=self.r, month=6)
            rolling['abs'] = rolling['corrcoef'].abs()
            fitted = rolling[rolling['abs'] == rolling['abs'].max()]
            coeff, step = fitted.iloc[0, 0], fitted.iloc[0, 1]
            self.__setattr__(
                '__coeffr',
                (coeff, self.r.index[-1 if step < 0 else 0] - self.r.index[step - 1 if step < 0 else step], step)
            )
        return self.__getattribute__('__coeffr')

    @property
    def coeff(self) -> float:
        """
        전체 시계열 상관계수
        """
        if not hasattr(self, '_coeff'):
            self.__setattr__('_coeff', self._j.corr().iloc[0, 1])
        return self.__getattribute__('_coeff')

    @property
    def coeffw(self) -> float:
        """
        기간 구별 가중 상관계수
        """
        if not hasattr(self, '_coeffw'):
            self.__setattr__('_coeffw', self.coeff if len(self._j) < 93 else weighted_corrcoeff(self._j).T.mean())
        return self.__getattribute__('_coeffw')

    @property
    def coeffr(self) -> float:
        """
        이동 상관계수
        """
        coeff, _, __ = self._coeffr()
        return coeff

    @property
    def coeffr_fb(self):
        _, fb, __ = self._coeffr()
        return fb

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
    def trace_rshift(self) -> go.Scatter:
        _, _, step = self._coeffr()
        return go.Scatter(
            x=self.r.shift(step).index, y=self.r.shift(step), name=f'{self._rname}<br>shifted',
            visible='legendonly', showlegend=True, mode='lines', line=dict(dash='dot'),
            xhoverformat='%Y/%m/%d', hovertemplate='%{x}<br>%{y}'
        )

    @property
    def trace_corr(self) -> go.Scatter:
        return go.Scatter(
            x=normalize(self.l, -1, 1), y=normalize(self.r, -1, 1), name='산포도',
            meta=self._j.index, text=self.l, customdata=self.r, mode='markers',
            hovertemplate='%{meta}<br>x = %{x}(%{text})<br>y = %{y}(%{customdata})<extra></extra>'
        )
    
    




if __name__ == "__main__":
    from tdatlib import stock, macro, market

    period = 20

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
    print(relation.by_period)
    # print(relation.corr)
    # print(relation.rolling_corr)
    # relation.display()