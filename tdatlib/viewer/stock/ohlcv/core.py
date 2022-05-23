from tdatlib.dataset.stock.ohlcv import technical
from tdatlib.viewer.tools import CD_RANGER
from tdatlib.dataset import tools
import plotly.graph_objects as go
import pandas as pd


class _price(object):

    def __init__(self, obj:technical):
        self._obj = obj

    def candle(self) -> go.Candlestick:
        if not hasattr(self, '__candle'):
            self.__setattr__(
                '__candle',
                go.Candlestick(
                    name='캔들 차트',
                    x=self._obj.ohlcv.index,
                    open=self._obj.ohlcv.시가,
                    high=self._obj.ohlcv.고가,
                    low=self._obj.ohlcv.저가,
                    close=self._obj.ohlcv.종가,
                    visible=True,
                    showlegend=True,
                    legendgrouptitle=dict(text='캔들 차트'),
                    increasing_line=dict(color='red'),
                    decreasing_line=dict(color='royalblue'),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',' if self._obj.currency == '원' else '.2f',
                )
            )
        return self.__getattribute__('__candle')

    def volume(self) -> go.Bar:
        if not hasattr(self, f'__volume'):
            self.__setattr__(
                f'__volume',
                go.Bar(
                    name='거래량',
                    x=self._obj.ohlcv.index,
                    y=self._obj.ohlcv.거래량,
                    marker=dict(color=self._obj.ohlcv.거래량.pct_change().apply(lambda x: 'blue' if x < 0 else 'red')),
                    visible=True,
                    showlegend=False,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',',
                    hovertemplate='%{x}<br>거래량: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__(f'__volume')

    def price(self, col:str) -> go.Scatter:
        if not hasattr(self, f'__{col}'):
            self.__setattr__(
                f'__{col}',
                go.Scatter(
                    name=col,
                    x=self._obj.ohlcv.index,
                    y=self._obj.ohlcv[col],
                    visible='legendonly',
                    showlegend=True,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',' if self._obj.currency == '원' else '.2f',
                    legendgrouptitle=dict(text='주가 차트') if col == '시가' else None,
                    hovertemplate='%{x}<br>' + col + ': %{y}' + self._obj.currency + '<extra></extra>'
                )
            )
        return self.__getattribute__(f'__{col}')

    def ma(self, col:str) -> go.Scatter:
        if not hasattr(self, f'__{col}'):
            self.__setattr__(
                f'__{col}',
                go.Scatter(
                    name=col,
                    x=self._obj.ohlcv_sma.index,
                    y=self._obj.ohlcv_sma[col],
                    visible='legendonly' if col in ['MA5D', 'MA10D', 'MA20D'] else True,
                    showlegend=True,
                    legendgrouptitle=dict(text='이동 평균선') if col == 'MA5D' else None,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',.0f',
                    hovertemplate='%{x}<br>' + col + ': %{y}' + self._obj.currency + '<extra></extra>'
                )
            )
        return self.__getattribute__(f'__{col}')

    def nc(self, col:str) -> go.Scatter:
        if not hasattr(self, f'__{col}'):
            self.__setattr__(
                f'__{col}',
                go.Scatter(
                    name=col,
                    x=self._obj.ohlcv_iir.index,
                    y=self._obj.ohlcv_iir[col],
                    visible='legendonly',
                    showlegend=True,
                    legendgrouptitle=dict(text='노이즈 제거선') if col == 'NC5D' else None,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',.0f',
                    hovertemplate='%{x}<br>' + col + ': %{y}' + self._obj.currency + '<extra></extra>'
                )
            )
        return self.__getattribute__(f'__{col}')

    def trend(self, col:str) -> go.Scatter:
        if not hasattr(self, f'__tr{col}'):
            tr = self._obj.ohlcv_trend[col].dropna()
            dx, dy = (tr.index[-1] - tr.index[0]).days, 100 * (tr[-1] / tr[0] - 1)
            slope = round(dy / dx, 2)
            self.__setattr__(
                f'__tr{col}',
                go.Scatter(
                    name=col.replace('M', '개월').replace('Y', '년'),
                    x=tr.index,
                    y=tr,
                    mode='lines',
                    line=dict(
                        width=2,
                        dash='dot'
                    ),
                    visible='legendonly',
                    showlegend=True,
                    legendgrouptitle=dict(text='평균 추세선') if col == '1M' else None,
                    hovertemplate=f'{col} 평균 추세 강도: {slope}[%/days]<extra></extra>'
                )
            )
        return self.__getattribute__(f'__tr{col}')

    def bound(self, col:str) -> tuple:
        if not hasattr(self, f'__bd{col}'):
            name = col.replace('M', '개월').replace('Y', '년')
            self.__setattr__(
                f'__bd{col}',
                (
                    go.Scatter(
                        name=f'{name}',
                        x=self._obj.ohlcv_bound.index,
                        y=self._obj.ohlcv_bound[col].resist,
                        mode='lines',
                        visible='legendonly',
                        showlegend=True,
                        legendgroup=col,
                        legendgrouptitle=dict(text='지지/저항선') if col == '2M' else None,
                        line=dict(dash='dot', color='blue'),
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',.0f',
                        hovertemplate='%{x}<br>저항: %{y}' + self._obj.currency + '<extra></extra>'
                    ),
                    go.Scatter(
                        name=f'{name}',
                        x=self._obj.ohlcv_bound.index,
                        y=self._obj.ohlcv_bound[col].support,
                        mode='lines',
                        visible='legendonly',
                        showlegend=False,
                        legendgroup=col,
                        line=dict(dash='dot', color='red'),
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',.0f',
                        hovertemplate='%{x}<br>지지: %{y}' + self._obj.currency + '<extra></extra>'
                    )
                )
            )
        return self.__getattribute__(f'__bd{col}')


class _bollinger(object):

    def __init__(self, obj:technical):
        self._obj = obj

    def obj_bband(self) -> list:
        if not hasattr(self, f'__objbband'):
            graphs = list()
            for n, col, label in [
                (0, 'upper2sd', '상단'),
                (1, 'mid', 'MA20'),
                (2, 'lower2sd', '하단')
            ]:
                graphs.append(go.Scatter(
                    name='볼린저밴드',
                    x=getattr(self._obj.ohlcv_bband, col).index,
                    y=getattr(self._obj.ohlcv_bband, col),
                    mode='lines',
                    line=dict(color='rgb(184, 247, 212)'),
                    fill='tonexty' if n > 0 else None,
                    visible=True,
                    showlegend=False if n > 0 else True,
                    legendgroup='볼린저밴드',
                    legendgrouptitle=None if n > 0 else dict(text='볼린저밴드'),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',.2f',
                    hovertemplate='%{x}<br>' + label + ': %{y}' + self._obj.currency + '<extra></extra>',
                ))
            self.__setattr__(f'__objbband', graphs)
        return self.__getattribute__(f'__objbband')

    def obj_bband_inner(self) -> list:
        if not hasattr(self, f'__objbbandinner'):
            graphs = list()
            for n, col, label in [
                (0, 'upper2sd', '상단'),
                (1, 'upper1sd', '상단1SD'),
                (2, 'lower1sd', '하단1SD'),
                (3, 'lower2sd', '하단')
            ]:
                color = {
                    '상단': 'rgb(248, 233, 184)',
                    '상단1SD': 'rgb(248, 233, 184)',
                    '하단1SD': 'rgb(248, 187, 184)',
                    '하단': 'rgb(248, 187, 184)',
                }
                graphs.append(go.Scatter(
                    name='상단밴드' if n < 2 else '하단밴드',
                    x=getattr(self._obj.ohlcv_bband, col).index,
                    y=getattr(self._obj.ohlcv_bband, col),
                    mode='lines',
                    line=dict(color=color[label]),
                    fill='tonexty' if n % 2 else None,
                    visible='legendonly',
                    showlegend=False if n % 2 else True,
                    legendgroup='상단밴드' if n < 2 else '하단밴드',
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',.2f',
                    hovertemplate='%{x}<br>' + label + ': %{y}' + self._obj.currency + '<extra></extra>',
                ))
            self.__setattr__('__objbbandinner', graphs)
        return self.__getattribute__(f'__objbbandinner')

    def obj_bband_width(self) -> go.Scatter:
        if not hasattr(self, f'__objbbandwidth'):
            self.__setattr__(
                f'__objbbandwidth',
                go.Scatter(
                    name='폭',
                    x=getattr(self._obj.ohlcv_bband, 'width').index,
                    y=getattr(self._obj.ohlcv_bband, 'width'),
                    visible=True,
                    showlegend=True,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>폭: %{y}%<extra></extra>'
                )
            )
        return self.__getattribute__('__objbbandwidth')

    def obj_bband_tag(self) -> go.Scatter:
        if not hasattr(self, f'__objbbandtag'):
            self.__setattr__(
                f'__objbbandtag',
                go.Scatter(
                    name='신호',
                    x=getattr(self._obj.ohlcv_bband, 'signal').index,
                    y=getattr(self._obj.ohlcv_bband, 'signal'),
                    visible=True,
                    showlegend=True,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>태그신호: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__objbbandtag')

    def obj_bband_contain(self) -> go.Scatter:
        if not hasattr(self, f'__objbbandcont'):
            self.__setattr__(
                f'__objbbandcont',
                go.Scatter(
                    name='내부밴드추세',
                    x=getattr(self._obj.ohlcv_bband, 'inner_band').index,
                    y=getattr(self._obj.ohlcv_bband, 'inner_band'),
                    visible=True,
                    showlegend=True,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>비율: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__(f'__objbbandcont')


class sketch(object):

    def __init__(self):
        self.__x_axis = dict(
            showticklabels=False,
            tickformat='%Y/%m/%d',
            zeroline=False,
            showgrid=True,
            gridcolor='lightgrey',
            autorange=True,
            showline=True,
            linewidth=1,
            linecolor='grey',
            mirror=False,
        )
        self.__y_axis = dict(
            showticklabels=True,
            zeroline=False,
            showgrid=True,
            gridcolor='lightgrey',
            autorange=True,
            showline=True,
            linewidth=0.5,
            linecolor='grey',
            mirror=False
        )

    def x_axis(self, title:str=str(), showticklabels:bool=False, rangeselector:bool=False) -> dict:
        _ = self.__x_axis.copy()
        if title:
            _['title'] = title
        if showticklabels:
            _['showticklabels'] = True
        if rangeselector:
            _['rangeselector'] = CD_RANGER
        return _

    def y_axis(self, title:str=str()) -> dict:
        _ = self.__y_axis.copy()
        if title:
            _['title'] = title
        return _

