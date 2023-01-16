from tdatlib.archive.deprecated.dataset.stock import technical
import plotly.graph_objects as go


class chart(object):

    def __init__(self, src:technical):
        self.src = src

    @property
    def candle(self) -> go.Candlestick:
        if not hasattr(self, '__candle'):
            self.__setattr__(
                '__candle',
                go.Candlestick(
                    name='캔들 차트',
                    x=self.src.ohlcv.index,
                    open=self.src.ohlcv.시가,
                    high=self.src.ohlcv.고가,
                    low=self.src.ohlcv.저가,
                    close=self.src.ohlcv.종가,
                    visible=True,
                    showlegend=True,
                    legendgrouptitle=dict(text='캔들 차트'),
                    increasing_line=dict(color='red'),
                    decreasing_line=dict(color='royalblue'),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',' if self.src.currency == '원' else '.2f',
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
                    x=self.src.ohlcv.index,
                    y=self.src.ohlcv.거래량,
                    marker=dict(color=self.src.ohlcv.거래량.pct_change().apply(lambda x: 'blue' if x < 0 else 'red')),
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
                        x=self.src.ohlcv.index,
                        y=self.src.ohlcv[col],
                        visible='legendonly',
                        showlegend=True,
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',' if self.src.currency == '원' else '.2f',
                        legendgrouptitle=dict(text='주가 차트') if col == '시가' else None,
                        hovertemplate='%{x}<br>' + col + ': %{y}' + self.src.currency + '<extra></extra>'
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
                        x=self.src.ohlcv_sma.index,
                        y=self.src.ohlcv_sma[col],
                        visible='legendonly' if col in ['MA5D', 'MA10D', 'MA20D'] else True,
                        showlegend=True,
                        legendgrouptitle=dict(text='이동 평균선') if col == 'MA5D' else None,
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',.0f',
                        hovertemplate='%{x}<br>' + col + ': %{y}' + self.src.currency + '<extra></extra>'
                    ) for col in self.src.ohlcv_sma.columns
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
                        x=self.src.ohlcv_iir.index,
                        y=self.src.ohlcv_iir[col],
                        visible='legendonly',
                        showlegend=True,
                        legendgrouptitle=dict(text='노이즈 제거선') if col == 'NC5D' else None,
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',.0f',
                        hovertemplate='%{x}<br>' + col + ': %{y}' + self.src.currency + '<extra></extra>'
                    ) for col in self.src.ohlcv_iir.columns
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
                        x=self.src.ohlcv_trend[col].index,
                        y=self.src.ohlcv_trend[col],
                        mode='lines',
                        line=dict(
                            width=2,
                            dash='dot'
                        ),
                        visible='legendonly',
                        showlegend=True,
                        legendgrouptitle=dict(text='평균 추세선') if col == '1M' else None,
                        meta=self.src.ohlcv_trend[f'{col}-Slope'],
                        hovertemplate=f'{col}' + ' 추세 강도: %{meta}[%/days]<extra></extra>'
                    ) for col in self.src.ohlcv_trend.columns if not col.endswith('Slope')
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
                            x=self.src.ohlcv_bound.index,
                            y=self.src.ohlcv_bound[col].resist,
                            mode='lines',
                            visible='legendonly',
                            showlegend=True,
                            legendgroup=col,
                            legendgrouptitle=dict(text='지지/저항선') if col == '2M' else None,
                            line=dict(dash='dot', color='blue'),
                            xhoverformat='%Y/%m/%d',
                            yhoverformat=',.0f',
                            hovertemplate='%{x}<br>저항: %{y}' + self.src.currency + '<extra></extra>'
                        ),
                        go.Scatter(
                            name=col.replace('M', '개월').replace('Y', '년'),
                            x=self.src.ohlcv_bound.index,
                            y=self.src.ohlcv_bound[col].support,
                            mode='lines',
                            visible='legendonly',
                            showlegend=False,
                            legendgroup=col,
                            line=dict(dash='dot', color='red'),
                            xhoverformat='%Y/%m/%d',
                            yhoverformat=',.0f',
                            hovertemplate='%{x}<br>지지: %{y}' + self.src.currency + '<extra></extra>'
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
                    x=getattr(self.src.ohlcv_bband, col).index,
                    y=getattr(self.src.ohlcv_bband, col),
                    mode='lines',
                    line=dict(color='rgb(184, 247, 212)'),
                    fill='tonexty' if n > 0 else None,
                    visible=True,
                    showlegend=False if n > 0 else True,
                    legendgroup='볼린저밴드',
                    legendgrouptitle=None if n > 0 else dict(text='볼린저밴드'),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',.2f',
                    hovertemplate='%{x}<br>' + label + ': %{y}' + self.src.currency + '<extra></extra>',
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
                    x=getattr(self.src.ohlcv_bband, col).index,
                    y=getattr(self.src.ohlcv_bband, col),
                    mode='lines',
                    line=dict(color=color[label]),
                    fill='tonexty' if n % 2 else None,
                    visible='legendonly',
                    showlegend=False if n % 2 else True,
                    legendgroup='상단밴드' if n < 2 else '하단밴드',
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',.2f',
                    hovertemplate='%{x}<br>' + label + ': %{y}' + self.src.currency + '<extra></extra>',
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
                    x=getattr(self.src.ohlcv_bband, 'width').index,
                    y=getattr(self.src.ohlcv_bband, 'width'),
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
                    x=getattr(self.src.ohlcv_bband, 'signal').index,
                    y=getattr(self.src.ohlcv_bband, 'signal'),
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
                    x=getattr(self.src.ohlcv_bband, 'inner_band').index,
                    y=getattr(self.src.ohlcv_bband, 'inner_band'),
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
            breakout = self.src.ohlcv_bband.squeeze_break
            breakout = breakout[breakout.est >= 90]
            breakout = self.src.ohlcv[self.src.ohlcv.index.isin(breakout.index)].copy()
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
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',d' if self.src.currency == '원' else '.2f',
                    hovertemplate='%{x}<br>S-B: %{y}' + self.src.currency + '<extra></extra>'
                )
            )
        return self.__getattribute__('__breakout')

    @property
    def macd(self) -> go.Scatter:
        if not hasattr(self, '__macd'):
            self.__setattr__(
                '__macd',
                go.Scatter(
                    name='MACD',
                    x=self.src.ohlcv_ta['trend_macd'].index,
                    y=self.src.ohlcv_ta['trend_macd'],
                    visible=True,
                    showlegend=True,
                    legendgroup='MACD',
                    legendgrouptitle=dict(text='MACD'),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>MACD: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__macd')

    @property
    def macd_sig(self) -> go.Scatter:
        if not hasattr(self, '__macdsig'):
            self.__setattr__(
                '__macdsig',
                go.Scatter(
                    name='Signal',
                    x=self.src.ohlcv_ta['trend_macd_signal'].index,
                    y=self.src.ohlcv_ta['trend_macd_signal'],
                    visible=True,
                    showlegend=True,
                    legendgroup='MACD',
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>Signal: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__macdsig')

    @property
    def macd_diff(self) -> go.Bar:
        if not hasattr(self, '__macddiff'):
            self.__setattr__(
                '__macddiff',
                go.Bar(
                    name='Diff',
                    x=self.src.ohlcv_ta['trend_macd_diff'].index,
                    y=self.src.ohlcv_ta['trend_macd_diff'],
                    visible=True,
                    showlegend=True,
                    legendgroup='MACD',
                    marker=dict(
                        color=['blue' if v <= 0 else 'red' for v in self.src.ohlcv_ta.trend_macd_diff.pct_change()]
                    ),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>Signal: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__macddiff')

    @property
    def rsi(self) -> go.Scatter:
        if not hasattr(self, '__rsi'):
            self.__setattr__(
                '__rsi',
                go.Scatter(
                    name='RSI',
                    x=self.src.ohlcv_ta['momentum_rsi'].index,
                    y=self.src.ohlcv_ta['momentum_rsi'],
                    visible=True,
                    showlegend=True,
                    legendgroup='RSI',
                    legendgrouptitle=dict(text='RSI'),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>RSI: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__rsi')

    @property
    def stoch_rsi(self) -> go.Scatter:
        if not hasattr(self, '__stoch_rsi'):
            self.__setattr__(
                '__stoch_rsi',
                go.Scatter(
                    name='(S)RSI',
                    x=self.src.ohlcv_ta['momentum_stoch'].index,
                    y=self.src.ohlcv_ta['momentum_stoch'],
                    visible=True,
                    showlegend=True,
                    legendgroup='RSI',
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>(S)RSI: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__stoch_rsi')

    @property
    def stoch_rsi_sig(self) -> go.Scatter:
        if not hasattr(self, '__stoch_rsi_sig'):
            self.__setattr__(
                '__stoch_rsi_sig',
                go.Scatter(
                    name='(S)RSI-Signal',
                    x=self.src.ohlcv_ta['momentum_stoch_signal'].index,
                    y=self.src.ohlcv_ta['momentum_stoch_signal'],
                    visible=True,
                    showlegend=True,
                    legendgroup='RSI',
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>(S)RSI-Sig: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__stoch_rsi_sig')

    @property
    def mfi(self) -> go.Scatter:
        if not hasattr(self, '__mfi'):
            self.__setattr__(
                '__mfi',
                go.Scatter(
                    name='MFI',
                    x=self.src.ohlcv_ta.volume_mfi.index,
                    y=self.src.ohlcv_ta.volume_mfi,
                    visible=True,
                    showlegend=True,
                    legendgroup='MFI',
                    legendgrouptitle=dict(text='MFI'),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>MFI: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__mfi')

    @property
    def cci(self) -> go.Scatter:
        if not hasattr(self, '__cci'):
            self.__setattr__(
                '__cci',
                go.Scatter(
                    name='CCI',
                    x=self.src.ohlcv_ta.trend_cci.index,
                    y=self.src.ohlcv_ta.trend_cci,
                    visible=True,
                    showlegend=True,
                    legendgroup='CCI',
                    legendgrouptitle=dict(text='CCI'),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>CCI: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__cci')

    @property
    def vortex(self) -> go.Scatter:
        if not hasattr(self, '__vortex'):
            self.__setattr__(
                '__vortex',
                go.Scatter(
                    name='Vortex',
                    x=self.src.ohlcv_ta.trend_vortex_ind_diff.index,
                    y=self.src.ohlcv_ta.trend_vortex_ind_diff,
                    visible=True,
                    showlegend=True,
                    legendgroup='Vortex',
                    legendgrouptitle=dict(text='Vortex'),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>Vortex: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__vortex')

    @property
    def trix(self) -> go.Scatter:
        if not hasattr(self, '__trix'):
            self.__setattr__(
                '__trix',
                go.Scatter(
                    name='Trix',
                    x=self.src.ohlcv_ta.trend_trix.index,
                    y=self.src.ohlcv_ta.trend_trix,
                    visible=True,
                    showlegend=True,
                    legendgroup='Trix',
                    legendgrouptitle=dict(text='Trix'),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>Trix: %{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__trix')

