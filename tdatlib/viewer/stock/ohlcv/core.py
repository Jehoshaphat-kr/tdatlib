from tdatlib.dataset.stock.ohlcv import technical
from tdatlib.viewer.tools import CD_RANGER
from tdatlib.dataset import tools
import plotly.graph_objects as go
import pandas as pd


class chart(object):

    def __init__(self, obj:technical):
        self._obj = obj

    @property
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

    @property
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

    @property
    def price(self) -> dict:
        if not hasattr(self, f'__price'):
            self.__setattr__(
                f'__price',
                {
                    col:go.Scatter(
                        name=col,
                        x=self._obj.ohlcv.index,
                        y=self._obj.ohlcv[col],
                        visible='legendonly',
                        showlegend=True,
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',' if self._obj.currency == '원' else '.2f',
                        legendgrouptitle=dict(text='주가 차트') if col == '시가' else None,
                        hovertemplate='%{x}<br>' + col + ': %{y}' + self._obj.currency + '<extra></extra>'
                    ) for col in ['시가', '고가', '저가', '종가']
                }
            )
        return self.__getattribute__(f'__price')

    @property
    def ma(self) -> dict:
        if not hasattr(self, f'__ma'):
            self.__setattr__(
                f'__ma',
                {
                    col: go.Scatter(
                        name=col,
                        x=self._obj.ohlcv_sma.index,
                        y=self._obj.ohlcv_sma[col],
                        visible='legendonly' if col in ['MA5D', 'MA10D', 'MA20D'] else True,
                        showlegend=True,
                        legendgrouptitle=dict(text='이동 평균선') if col == 'MA5D' else None,
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',.0f',
                        hovertemplate='%{x}<br>' + col + ': %{y}' + self._obj.currency + '<extra></extra>'
                    ) for col in self._obj.ohlcv_sma.columns
                }
            )
        return self.__getattribute__(f'__ma')

    @property
    def nc(self) -> dict:
        if not hasattr(self, f'__nc'):
            self.__setattr__(
                f'__nc',
                {
                    col:go.Scatter(
                        name=col,
                        x=self._obj.ohlcv_iir.index,
                        y=self._obj.ohlcv_iir[col],
                        visible='legendonly',
                        showlegend=True,
                        legendgrouptitle=dict(text='노이즈 제거선') if col == 'NC5D' else None,
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',.0f',
                        hovertemplate='%{x}<br>' + col + ': %{y}' + self._obj.currency + '<extra></extra>'
                    ) for col in self._obj.ohlcv_iir.columns
                }
            )
        return self.__getattribute__(f'__nc')

    @property
    def trend(self) -> dict:
        if not hasattr(self, f'__trend'):
            self.__setattr__(
                f'__trend',
                {
                    col:go.Scatter(
                        name=col.replace('M', '개월').replace('Y', '년'),
                        x=self._obj.ohlcv_trend[col].index,
                        y=self._obj.ohlcv_trend[col],
                        mode='lines',
                        line=dict(
                            width=2,
                            dash='dot'
                        ),
                        visible='legendonly',
                        showlegend=True,
                        legendgrouptitle=dict(text='평균 추세선') if col == '1M' else None,
                        meta=self._obj.ohlcv_trend[f'{col}-Slope'],
                        hovertemplate=f'{col}' + ' 추세 강도: %{meta}[%/days]<extra></extra>'
                    ) for col in self._obj.ohlcv_trend.columns if not col.endswith('Slope')
                }
            )
        return self.__getattribute__(f'__trend')

    @property
    def bound(self) -> dict:
        if not hasattr(self, f'__bound'):
            self.__setattr__(
                f'__bound',
                {
                    col:(
                        go.Scatter(
                            name=col.replace('M', '개월').replace('Y', '년'),
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
                            name=col.replace('M', '개월').replace('Y', '년'),
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
                    ) for col in ['2M', '3M', '6M', '1Y']
                }
            )
        return self.__getattribute__(f'__bound')

    @property
    def bb(self) -> list:
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

    @property
    def bb_inner(self) -> list:
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

    @property
    def bb_width(self) -> go.Scatter:
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

    @property
    def bb_tag(self) -> go.Scatter:
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

    @property
    def bb_contain(self) -> go.Scatter:
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

    @property
    def bb_breakout(self) -> go.Scatter:
        if not hasattr(self, '__breakout'):
            breakout = self._obj.ohlcv_bband.squeeze_break
            breakout = breakout[breakout.est >= 90]
            breakout = self._obj.ohlcv[self._obj.ohlcv.index.isin(breakout.index)].copy()
            self.__setattr__(
                '__breakout',
                go.Scatter(
                    name='Breakout',
                    x=breakout.index,
                    y=breakout.종가,
                    mode='markers',
                    marker=dict(
                        symbol='triangle-up',
                        color='yellow',
                        size=8
                    ),
                    visible='legendonly',
                    showlegend=True,
                    legendgrouptitle=dict(text='평가지표'),
                    xhoverformat='%Y%m%d',
                    yhoverformat=',d' if self._obj.currency == '원' else '.2f',
                    hovertemplate='%{x}<br>S-B: %{y}' + self._obj.currency + '<extra></extra>'
                )
            )
        return self.__getattribute__('__breakout')



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

